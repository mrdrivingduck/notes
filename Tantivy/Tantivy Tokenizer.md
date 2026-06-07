# Tantivy - Tokenizer

Created by: Mr Dk.

Co-authored by: Claude Opus 4.6

2026 / 06 / 05 23:00

Hangzhou, Zhejiang, China

---

## 背景

在全文搜索里，原始文本通常不能直接进入倒排索引。索引真正关心的是一个个独立的词项（term），所以写入索引之前，需要先把文本切成一串 token。这个过程就是 **分词（tokenization）**。

分词看起来只是"切字符串"，但它会直接影响搜索效果。最简单的做法是按空格切分；实际场景里还会叠加很多处理：把大写转成小写，让搜索对大小写不敏感；去掉 "the"、"is" 这类停用词；把 "running" 归一化成 "run" 这样的词干；对于中文这类没有天然空格分隔的语言，还需要基于词典或模型做分词。

Tantivy 把这件事抽象成一条流水线：前面是一个基础分词器（Tokenizer），后面可以接若干个过滤器（Token Filter）。Tokenizer 负责把文本切开，Filter 负责继续加工这些 token。每一层都只做一件事，因此可以自由组合、替换。Tantivy 内置了一批常用实现，也把核心接口做成公开 trait，方便用户和社区扩展。

## 分词流水线：整体结构

先看一段文本从输入到最终写入倒排索引的大致路径：

```
原始文本 "Hello, the WORLD! Welcome here."
  │
  ▼
┌───────────────────────────┐
│  Tokenizer                │  切分文本 → 产生 token 流
│  (e.g. SimpleTokenizer)   │
└───────────────────────────┘
  │  "Hello" → "the" → "WORLD" → "Welcome" → "here"
  ▼
┌───────────────────────────┐
│  TokenFilter 1            │  变换每个 token（转小写）
│  (e.g. LowerCaser)        │
└───────────────────────────┘
  │  "hello" → "the" → "world" → "welcome" → "here"
  ▼
┌───────────────────────────┐
│  TokenFilter 2            │  过滤掉某些 token（去停用词）
│  (e.g. StopWordFilter)    │
└───────────────────────────┘
  │  "hello" → "world" → "welcome" → "here"
  ▼
写入倒排索引
```

这条链路里有三个最核心的抽象：

- `Tokenizer`：流水线的起点，负责把原始文本切成 token。
- `TokenStream`：Tokenizer 的输出，本质上是一个可迭代的 token 流。调用方通过 `advance()` 推进到下一个 token，再用 `token()` 读取当前 token 的内容。
- `TokenFilter`：流水线的中间节点，采用装饰器模式。它接收一个上游 Tokenizer，包装后产出一个新的 Tokenizer：新的 `TokenStream` 在迭代时会对上游 token 做变换，比如转小写；也可以做过滤，比如跳过停用词。

### 组装流水线：TextAnalyzer

Tantivy 用 `TextAnalyzer` 表示一条完整的分析流水线。它的 builder 接收一个基础 Tokenizer，然后依次在链条上追加若干 TokenFilter：

```rust
let analyzer = TextAnalyzer::builder(SimpleTokenizer::default())
    .filter(RemoveLongFilter::limit(40))
    .filter(LowerCaser)
    .filter(Stemmer::new(Language::English))
    .build();
```

每调用一次 `.filter()`，都会通过 `TokenFilter::transform()` 把当前 Tokenizer 再包一层，于是形成一条嵌套的类型链。最后 `.build()` 通过 `BoxableTokenizer` 做类型擦除，把整条流水线封装成统一的 `TextAnalyzer` 类型。

### 注册与查找：TokenizerManager

`TokenizerManager` 可以理解为一个线程安全的 `HashMap<String, TextAnalyzer>`。每个索引实例都有自己的 manager，所以不同索引可以注册不同的分析器。使用时通过字符串名字注册和查找：

```rust
// 注册自定义 tokenizer
index.tokenizers().register("my_analyzer", analyzer);

// 在 Schema 中引用
let text_field_indexing = TextFieldIndexing::default()
    .set_tokenizer("my_analyzer")
    .set_index_option(IndexRecordOption::WithFreqsAndPositions);
```

默认构造的 `TokenizerManager` 会预先注册四个内置分析器：`raw`、`default`、`en_stem`、`whitespace`。这些名字可以在 schema 中直接引用，不需要用户额外注册。

## 接口定义

Tantivy 把分词相关的核心接口放在独立的 `tantivy-tokenizer-api` crate 中。这样第三方实现自定义分词器时，只需要依赖这个很轻的 API crate，不必把完整的 tantivy 拉进来。

### Token

`Token` 是分词后的最小单元，里面除了文本本身，还保存了偏移和位置信息：

```rust
pub struct Token {
    pub offset_from: usize,
    pub offset_to: usize,
    pub position: usize,
    pub text: String,
    pub position_length: usize,
}
```

- `offset_from` / `offset_to`：token 在原始文本中的字节偏移范围，主要用于回溯原文，比如搜索结果高亮。
- `position`：token 在流中的序号。当 TokenFilter 跳过某些 token 时，position 会出现跳跃，搜索引擎可以据此知道两个 token 中间是否省略了词。这对短语查询很重要。
- `text`：token 的实际文本内容。
- `position_length`：这个 token 跨越了多少个 position，通常为 1。当多个词被折叠成一个 token 时，这个值会大于 1。比如把 "New York City" 折叠成 "NYC"，那么 "NYC" 的 `position_length` 就是 3，表示它覆盖了原本 3 个位置。短语匹配需要这个信息来正确计算 token 之间的距离。

### Tokenizer trait

```rust
pub trait Tokenizer: 'static + Clone + Send + Sync {
    type TokenStream<'a>: TokenStream;
    fn token_stream<'a>(&'a mut self, text: &'a str) -> Self::TokenStream<'a>;
}
```

`Tokenizer` 只有一个函数：`token_stream()`。它接收原始文本，返回一个 `TokenStream`。实际实现中，Tokenizer 通常会预先持有一个 `Token` 缓冲区，交给 `TokenStream` 反复复用，避免每产出一个 token 就分配一次内存。

### TokenStream trait

```rust
pub trait TokenStream {
    fn advance(&mut self) -> bool;
    fn token(&self) -> &Token;
    fn token_mut(&mut self) -> &mut Token;
}
```

`TokenStream` 就是 token 流的迭代器：

- `advance()`：推进到下一个 token，返回 `false` 表示流结束。
- `token()`：读取当前 token。
- `token_mut()`：获取当前 token 的可变引用，供 TokenFilter 在迭代过程中修改内容。

### TokenFilter trait

```rust
pub trait TokenFilter: 'static + Send + Sync {
    type Tokenizer<T: Tokenizer>: Tokenizer;
    fn transform<T: Tokenizer>(self, tokenizer: T) -> Self::Tokenizer<T>;
}
```

`TokenFilter` 的核心就是 `transform()`：接收一个上游 `Tokenizer`，返回一个新的 `Tokenizer`。这正是装饰器模式的用法：每层过滤器包住上一层，最终形成嵌套结构。新 Tokenizer 产出的 token 流会先从上游拿 token，再做变换、过滤或扩展。

## 实现 Tokenizer：以 WhitespaceTokenizer 为例

`WhitespaceTokenizer` 是最简单的内置分词器之一：它按 ASCII 空白字符切分文本，并保留标点符号。用它来看 `Tokenizer` 的实现方式比较合适，因为逻辑足够小，能把接口本身看清楚。

先看 Tokenizer 和 TokenStream 两个结构体：

```rust
#[derive(Clone, Default)]
pub struct WhitespaceTokenizer {
    token: Token,  // 复用的 Token 缓冲区，避免反复分配
}

pub struct WhitespaceTokenStream<'a> {
    text: &'a str,          // 原始文本
    chars: CharIndices<'a>, // 字符迭代器，记录当前扫描位置
    token: &'a mut Token,   // 指向 Tokenizer 中复用的 Token
}
```

`WhitespaceTokenizer` 内部预分配了一个 `Token`。每次调用 `token_stream()` 时，它先把这个 token 重置，然后借给 `WhitespaceTokenStream` 使用。这样整个分词过程里只有一个 `Token` 实例被反复写入，不会额外产生一堆临时对象。

实现 `Tokenizer` trait：

```rust
impl Tokenizer for WhitespaceTokenizer {
    type TokenStream<'a> = WhitespaceTokenStream<'a>;

    fn token_stream<'a>(&'a mut self, text: &'a str) -> WhitespaceTokenStream<'a> {
        self.token.reset();
        WhitespaceTokenStream {
            text,
            chars: text.char_indices(),
            token: &mut self.token,
        }
    }
}
```

接下来是 `TokenStream` 的实现。核心逻辑都在 `advance()` 里：逐字符扫描，先跳过空白字符；遇到非空白字符后，再找到当前 token 的结束位置，也就是下一个空白字符的位置。随后把这段文本的偏移和内容写入 `Token`，返回 `true`。如果字符迭代器已经耗尽，就返回 `false`，表示流结束。

```rust
impl TokenStream for WhitespaceTokenStream<'_> {
    fn advance(&mut self) -> bool {
        self.token.text.clear();
        self.token.position = self.token.position.wrapping_add(1);
        while let Some((offset_from, c)) = self.chars.next() {
            if !c.is_ascii_whitespace() {
                let offset_to = self.search_token_end();
                self.token.offset_from = offset_from;
                self.token.offset_to = offset_to;
                self.token.text.push_str(&self.text[offset_from..offset_to]);
                return true;
            }
        }
        false
    }
    // ...
}
```

以 `"Hello, happy tax payer!"` 为输入，`WhitespaceTokenizer` 会产出四个 token：

| position | text     | offset_from | offset_to |
| -------- | -------- | ----------- | --------- |
| 0        | `Hello,` | 0           | 6         |
| 1        | `happy`  | 7           | 12        |
| 2        | `tax`    | 13          | 16        |
| 3        | `payer!` | 17          | 23        |

注意 `Hello,` 和 `payer!` 都保留了标点。这正是 `WhitespaceTokenizer` 和 `SimpleTokenizer` 的区别：`SimpleTokenizer` 按 `!char.is_alphanumeric()` 分割，标点会被去除掉。

## 实现 TokenFilter：以 StopWordFilter 为例

`StopWordFilter` 是一个典型的过滤型 TokenFilter。它维护一个停用词集合，在 token 流中跳过命中的 token。用它来看 TokenFilter 的装饰器模式会比较直观。

先看 `StopWordFilter` 本身，以及它对 `TokenFilter` 的实现：

```rust
#[derive(Clone)]
pub struct StopWordFilter {
    words: Arc<FxHashSet<String>>,
}

impl TokenFilter for StopWordFilter {
    type Tokenizer<T: Tokenizer> = StopWordFilterWrapper<T>;

    fn transform<T: Tokenizer>(self, tokenizer: T) -> StopWordFilterWrapper<T> {
        StopWordFilterWrapper {
            words: self.words,
            inner: tokenizer,
        }
    }
}
```

`transform()` 做的事情很简单：把自身携带的停用词集合和上游 Tokenizer 一起打包进 `StopWordFilterWrapper`。这个 Wrapper 自己也实现了 `Tokenizer`：

```rust
#[derive(Clone)]
pub struct StopWordFilterWrapper<T> {
    words: Arc<FxHashSet<String>>,
    inner: T,
}

impl<T: Tokenizer> Tokenizer for StopWordFilterWrapper<T> {
    type TokenStream<'a> = StopWordFilterStream<T::TokenStream<'a>>;

    fn token_stream<'a>(&'a mut self, text: &'a str) -> Self::TokenStream<'a> {
        StopWordFilterStream {
            words: self.words.clone(),
            tail: self.inner.token_stream(text),
        }
    }
}
```

这里的关键在 `token_stream()`：它先调用上游的 `inner.token_stream(text)` 拿到原始 token 流，再把这条流包进 `StopWordFilterStream`。这就是装饰器的嵌套方式：外层调用内层，内层继续调用自己的内层，一层层把 token 流串起来。

最后看 `StopWordFilterStream` 如何实现 `TokenStream`。核心仍然在 `advance()`：

```rust
impl<T: TokenStream> TokenStream for StopWordFilterStream<T> {
    fn advance(&mut self) -> bool {
        while self.tail.advance() {
            if !self.words.contains(&self.tail.token().text) {
                return true;
            }
        }
        false
    }
    // ...
}
```

每次调用 `advance()` 时，它会不断推进上游 token 流，直到遇到一个不在停用词集合中的 token 才返回 `true`。如果上游已经耗尽，就返回 `false`。

被过滤掉的 token 不会出现在下游，但它原本占据的位置不会被重排。因为 `position` 已经由上游 Tokenizer 递增设置，`StopWordFilter` 并不修改它，所以剩下的 token position 可能会出现跳跃，比如 `0, 1, 3`。这个细节对短语查询很重要：position 间距可以告诉搜索引擎，中间有词被跳过。

### TokenFilter 的模式

从 Tantivy 内置的 TokenFilter 可以归纳出三类实现模式：

- **变换型**：修改每个 token，但不改变 token 数量。比如 `LowerCaser` 把文本转成小写，`Stemmer` 把文本替换成词干。它们的 `advance()` 通常是调用一次上游 `advance()`，然后修改 `token_mut().text`，一进一出。
- **过滤型**：根据条件跳过某些 token。比如 `StopWordFilter` 跳过停用词，`AlphaNumOnlyFilter` 跳过非字母数字的 token，`RemoveLongFilter` 跳过超长 token。它们的 `advance()` 会在循环中反复调用上游 `advance()`，直到找到一个满足条件的 token。
- **扩展型**：把一个 token 展开成多个 token。比如同义词扩展可以把 "quick" 同时产出为 "quick" 和 "fast"。实现上通常会在 Filter 内部维护一个缓冲区：一次上游 `advance()` 产生多个候选 token，后续调用再从缓冲区里依次返回。扩展出的 token 可以共享相同的 `position`，表示它们处在同一个位置。Tantivy 内置没有这类 TokenFilter，但接口本身可以支持。

## 内置实现与社区扩展

### 内置 Tokenizer

Tantivy 内置的 Tokenizer 覆盖了一些最常见的场景：

| 类型                  | 行为                                                        |
| --------------------- | ----------------------------------------------------------- |
| `SimpleTokenizer`     | 按非字母数字字符（`!char.is_alphanumeric()`）分割，去掉标点 |
| `RawTokenizer`        | 不分词，整段文本作为单个 token                              |
| `WhitespaceTokenizer` | 按 ASCII 空白字符分割，保留标点                             |
| `NgramTokenizer`      | 将文本切为指定长度范围的 N-gram                             |
| `RegexTokenizer`      | 按正则表达式匹配切分                                        |
| `FacetTokenizer`      | 按 `/` 切分面搜索路径（如 `/electronics/phones`）           |

### 内置 TokenFilter

Filter 则更多是对 token 做后处理：

| 类型                 | 行为                                           | 模式   |
| -------------------- | ---------------------------------------------- | ------ |
| `LowerCaser`         | 将 token 文本转为小写                          | 变换型 |
| `RemoveLongFilter`   | 去掉超过指定字节长度的 token                   | 过滤型 |
| `Stemmer`            | 词干提取，支持 18 种语言                       | 变换型 |
| `StopWordFilter`     | 过滤停用词                                     | 过滤型 |
| `AlphaNumOnlyFilter` | 只保留纯字母数字的 token                       | 过滤型 |
| `AsciiFoldingFilter` | 将 Unicode 字符映射为 ASCII 等价物（如 é → e） | 变换型 |
| `SplitCompoundWords` | 基于词典拆分复合词（如德语）                   | 变换型 |

### 社区第三方扩展

由于 Tantivy 把核心接口抽到了独立的 `tantivy-tokenizer-api` crate 中，第三方可以只依赖这层 API 实现自己的分词器，不需要依赖完整的 tantivy。社区里已经有一些现成实现：

- [tantivy-jieba](https://github.com/jiegec/tantivy-jieba)：基于结巴分词的中文 Tokenizer，是比较常见的中文分词方案。
- [cang-jie](https://github.com/DCjanus/cang-jie)：基于 CEDICT 词典的中文 Tokenizer。

对于更特化的需求，比如拼音展开、同义词扩展，也可以通过自定义 `TokenFilter` 实现：在 `advance()` 中把一个 token 转换或展开成多个 token。这样不需要修改基础 Tokenizer，只要在流水线末尾追加新的 filter 即可。

## 参考资料

- [Tantivy GitHub Repository](https://github.com/quickwit-oss/tantivy)
- [tantivy-tokenizer-api Crate](https://github.com/quickwit-oss/tantivy/tree/main/tokenizer-api)
