# Web - OpenAPI Specification

Created by : Mr Dk.

2019 / 09 / 28 12:34

Nanjing, Jiangsu, China

---

## Background

__OpenAPI Specification (OAS)__，以前叫做 _Swagger_ 标准

是用于描述 RESTful Web 服务的接口文件

可以对接口进行描述、可视化等等

在 2016 年从 Swagger 项目中独立出来称为独立项目

版本：

* 2017-07-26: OpenAPI 3.0.0+
* 2014-09-08: Swagger 2.0
* 2012-08-22: Swagger 1.1
* ...

算是 RESTful 的世界标准？

> 好吧，接触过的几个 RESTful 的应用一个都没有使用 OAS

但毕竟是 RESTful 领域中的官方标准了

最近又准备做一做 RESTful fuzzing

所以研究了一下 OAS 的文档并做一些梳理

---

## Concept

OpenAPI 文档中经常用到一些概念

### OpenAPI Document

用于形容 API 的文档

### Path Templating

使用 `{}` 来标识路径中可被替换的部分

### Media Types

服从 RFC6838

* `text/plain; charset=utf-8`
* `application/json`
* ...

### HTTP Status Code

服从 RFC7231

### Specification Versions

一般来说是 `OAS 3.*.*`

在 API 文档中有一个字段需要注明标准的版本

### Format

JSON 格式或 YAML 格式

大小写除非特殊说明，否则都是敏感的

* 这个只要平时做事足够规范，取名足够合理，通常不会有什么问题

### Documentation Structure

根 API 文档建议命名为 `openapi.json` 或 `openapi.yaml`

---

## Schema

### OpenAPI Object

OpenAPI 文档的 root document

| Field Name   | Type                            | Description                                     |
| ------------ | ------------------------------- | ----------------------------------------------- |
| openapi      | string                          | OAS version                                     |
| info         | Info Object                     | Metadata of API (描述 API 的具体信息，之后展开) |
| servers      | [ Server Object ]               | 服务器的连接信息                                |
| paths        | Paths Object                    | API 路径                                        |
| components   | Components Object               | 该 OAS 中预定义的一些 Schema                    |
| security     | [ Security Requirement Object ] | 安全机制                                        |
| tags         | [ Tag Object ]                  | 额外的 metadata                                 |
| externalDocs | External Documentation Object   | 额外的文档                                      |

接下来先解决其中的几个简单的对象

### Server Object

| Field Name  | Type                                | Description                                      |
| ----------- | ----------------------------------- | ------------------------------------------------ |
| url         | string                              | 指向目标服务器的 URL                             |
| description | string                              | 用于描述这个服务器 (似乎还支持 Markdown)         |
| variables   | Map<string, Server Variable Object> | 变量名 + 变量值，用于替换 URL 中的 path template |

### Server Variable Object

| Field Names            | Type       | Description       |
| ---------------------- | ---------- | ----------------- |
| enum                   | [ string ] | 变量的所有可选值  |
| default (**REQUIRED**) | string     | 变量默认值        |
| description            | string     | Markdown 支持的哦 |

```json
{
  "servers": [
    {
      "url": "https://{username}.gigantic-server.com:{port}/{basePath}",
      "description": "The production API server",
      "variables": {
        "username": {
          "default": "demo",
          "description": "this value is assigned by the service provider, in this example `gigantic-server.com`"
        },
        "port": {
          "enum": [
            "8443",
            "443"
          ],
          "default": "8443"
        },
        "basePath": {
          "default": "v2"
        }
      }
    }
  ]
}
```

### Path Object

| Field Name | Type             | Description         |
| ---------- | ---------------- | ------------------- |
| /{path}    | Path Item Object | Endpoint 的相对路径 |

### Path Item Object

| Field Name  | Type                                     | Description                                |
| ----------- | ---------------------------------------- | ------------------------------------------ |
| $ref        | string                                   | 该对象可以被定义在外部                     |
| summary     | string                                   |                                            |
| description | string                                   | Markdown ✔                                 |
| get         | Operation Object                         | 定义了该路径下 GET 的操作                  |
| put         | Operation Object                         | 定义了该路径下 PUT 的操作                  |
| post        | Operation Object                         | 定义了该路径下 POST 的操作                 |
| delete      | Operation Object                         | 定义了该路径下 DELETE 的操作               |
| options     | Operation Object                         | 定义了该路径下 OPTIONS 的操作              |
| head        | Operation Object                         | 定义了该路径下 HEAD 的操作                 |
| patch       | Operation Object                         | 定义了该路径下 PATCH 的操作                |
| trace       | Operation Object                         | 定义了该路径下 TRACE 的操作                |
| servers     | [ Server Object ]                        | 可被替换的服务器，用于服务该路径的所有操作 |
| parameters  | [ Parameter Object \| Reference Object ] | 在以上操作中可被使用的参数                 |

```json
{
  "/pets": {
    "get": {},
    "parameters": [
      {}
    ]
  }
}
```

### Operation Object

描述某一路径上的某一 API

| Field Name   | Type                                             | Description                       |
| ------------ | ------------------------------------------------ | --------------------------------- |
| tags         | [ string ]                                       | 标签，用于 API 文档控制           |
| summary      | string                                           |                                   |
| description  | string                                           |                                   |
| externalDocs | External Documentation Object                    | 额外的外部文档                    |
| operationId  | string                                           | 用于识别这个操作的唯一标识        |
| parameters   | [ Parameter Object \| Reference Object ]         | 在本操作中可被使用的参数          |
| requestBody  | [ Request Body Object \| Reference Object ]      | RFC7231 HTTP 1.1 标准             |
| responses    | Responses Object                                 | 所有可能的回应                    |
| callBacks    | Map<string, Callback Object \| Reference Object> | 与 Operation 相关的回调           |
| deprecated   | boolean                                          |                                   |
| security     | [ Security Requirement Object ]                  |                                   |
| servers      | [ Server Object ]                                | 会覆盖 root document 中的 servers |

```json
{
  "tags": [
    "pet"
  ],
  "summary": "Updates a pet in the store with form data",
  "operationId": "updatePetWithForm",
  "parameters": [
      {}
  ],
  "requestBody": {},
  "responses": {},
  "security": [
    {
      "petstore_auth": [
        "write:pets",
        "read:pets"
      ]
    }
  ]
}
```

### Media Type Object

| Field Name | Type                                            | Descirption                                                  |
| ---------- | ----------------------------------------------- | ------------------------------------------------------------ |
| schema     | Schema Object \| Reference Object               | 定义 request, response, parameter 内容                       |
| example    |                                                 |                                                              |
| examples   | Map<string, Example Object \| Reference Object> |                                                              |
| encoding   | Map<string, Encoding Object>                    | The key, being the property name, MUST exist in the schema as a property |

```json
{
  "application/json": {
    "schema": {
      "$ref": "#/components/schemas/Pet"
    },
    "examples": {
      "cat": {
        "summary": "An example of a cat",
        "value": {
          "name": "Fluffy",
          "petType": "Cat",
          "color": "White",
          "gender": "male",
          "breed": "Persian"
        }
      },
      "dog": {
        "summary": "An example of a dog with a cat's name",
        "value": {
          "name": "Puma",
          "petType": "Dog",
          "color": "Black",
          "gender": "Female",
          "breed": "Mixed"
        }
      },
      "frog": {
        "$ref": "#/components/examples/frog-example"
      }
    }
  }
}
```

### Request Body Object

| Field Name             | Type                           | Description                          |
| ---------------------- | ------------------------------ | ------------------------------------ |
| description            | string                         |                                      |
| content (__REQUIRED__) | Map<string, Media Type Object> | 定义了对于每种请求 Media Type 的处理 |
| required               | boolean                        | 该请求体是否必须存在于请求中         |

```json
{
  "description": "user to add to the system",
  "content": {
    "application/json": {},
    "application/xml": {},
    "text/plain": {},
    "*/*": {}
  }
}
```

### Responses Object

| Field Name | Type                                | Description                      |
| ---------- | ----------------------------------- | -------------------------------- |
| default    | Response Object \| Reference Object | 对未指定的 HTTP 请求码的默认操作 |

### Response Object

| Field Name  | Type                                           | Description                              |
| ----------- | ---------------------------------------------- | ---------------------------------------- |
| description | string                                         |                                          |
| headers     | Map<string, Header Object \| Reference Object> | 响应头部？                               |
| content     | Map<string, Media Type Object>                 | 对于特定 Media Type 的响应内容           |
| links       | Map<string, Link Object \| Reference Object>   | 从 response 中可以被继续运行的 operation |

```json
{
  "responses": {
    "200": {
      "description": "Pet updated.",
      "content": {
        "application/json": {},
        "application/xml": {}
      }
    },
    "405": {
      "description": "Method Not Allowed",
      "content": {
        "application/json": {},
        "application/xml": {}
      }
    },
    "default": {
      "description": "Unexpected error",
      "content": {
        "application/json": {}
      }
    }
  }
}
```

### Parameter Object

定义某一个操作需要使用的参数

参数由 __name__ 和 __location__ 唯一确定

Location 是参数在请求中的位置

* path - 参数值是操作 URL 的一部分 - `/items/{itemId}`
* query - 参数值是附加在 URL 尾部 - `/items?id=###`
* header - 参数值位于请求头中
* cookie - 参数位于 cookie 中

| Field Name          | Type                                            | Description                                                  |
| ------------------- | ----------------------------------------------- | ------------------------------------------------------------ |
| name (__REQUIRED__) | string                                          | 参数名                                                       |
| in (__REQUIRED__)   | string                                          | 参数的位置 (location)                                        |
| description         | string                                          |                                                              |
| required            | boolean                                         |                                                              |
| deprecated          | boolean                                         |                                                              |
| allEmptyValue       | boolean                                         |                                                              |
| style               | string                                          | 决定参数如何被序列化                                         |
| explode             | boolean                                         | 如果为 `true`，参数值会将 array 中的每一个值和对象中的每对 key-pair 分开 |
| allowReserved       | boolean                                         | 决定参数中是否允许 RFC3986 中定义的保留字符                  |
| schema              | Schema Object \| Reference Object               | 定义了参数的类型                                             |
| example             |                                                 |                                                              |
| examples            | Map<string, Example Object \| Reference Object> |                                                              |
| content             | Map<string, Media Type Object>                  | MUST only contain one entry && A parameter MUST contain either a `schema` property, or a `content` property, but not both |

带 schema 的例子：

```json
{
  "name": "id",
  "in": "query",
  "description": "ID of the object to fetch",
  "required": false,
  "schema": {
    "type": "array",
    "items": {
      "type": "string"
    }
  },
  "style": "form",
  "explode": true
}
```

带 content 的例子：

```json
{
  "in": "query",
  "name": "coordinates",
  "content": {
    "application/json": {
      "schema": {
        "type": "object",
        "required": [
          "lat",
          "long"
        ],
        "properties": {
          "lat": {
            "type": "number"
          },
          "long": {
            "type": "number"
          }
        }
      }
    }
  }
}
```

### Schema Object

定义输入/输出的数据类型

可以是原生数据类型，也可以是对象或数组

| Field Name    | Type                          | Description  |
| ------------- | ----------------------------- | ------------ |
| nullable      | boolean                       | 是否允许空值 |
| discriminator | Discriminator                 | 支持多态？   |
| readOnly      | boolean                       |              |
| writeOnly     | boolean                       |              |
| xml           | XML Object                    |              |
| externalDocs  | External Documentation Object |              |
| example       |                               |              |
| deprecated    | boolean                       |              |

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64"
    },
    "name": {
      "type": "string"
    }
  },
  "required": [
    "name"
  ],
  "example": {
    "name": "Puma",
    "id": 1
  }
}
```

> 嗯？？？咋例子和表格对不上呢？ 🤨

### Reference Object

| Field Name          | Type   | Description          |
| ------------------- | ------ | -------------------- |
| $ref (__REQUIRED__) | string | The reference string |

```json
{
  "$ref": "#/components/schemas/Pet"
}
```

### Components Object

定义 OAS 中的一些可重用对象

| Field Name      | Type                                                    | Description |
| --------------- | ------------------------------------------------------- | ----------- |
| schemas         | Map<string, Schema Object \| Reference Object>          |             |
| responses       | Map<string, Response Object \| Reference Object>        |             |
| parameters      | Map<string, Parameter Object \| Reference Object>       |             |
| examples        | Map<string, Example Object \| Reference Object>         |             |
| requestBodies   | Map<string, Request Body Object \| Reference Object>    |             |
| headers         | Map<string, Header Object \| Reference Object>          |             |
| securitySchemes | Map<string, Security Scheme Object \| Reference Object> |             |
| links           | Map<string, Link Object \| Reference Object>            |             |
| callbacks       | Map<string, Callback Object \| Reference Object>        |             |

### Tag Object

| Field Name   | Type                          | Description |
| ------------ | ----------------------------- | ----------- |
| name         | string                        |             |
| description  | string                        |             |
| externalDocs | External Documentation Object |             |

```json
{
  "name": "pet",
  "description": "Pets operations"
}
```

### External Documentation Object

| Field Name  | Type   | Description                         |
| ----------- | ------ | ----------------------------------- |
| description | string |                                     |
| url         | string | The URL of the target documentation |

```json
{
  "description": "Find more info here",
  "url": "https://example.com"
}
```

### Info Object

| Field Name             | Type           | Description                          |
| ---------------------- | -------------- | ------------------------------------ |
| title (__REQUIRED__)   | string         | The title of the application         |
| description            | string         | 对于 app 的描述                      |
| termsOfService         | string         | API Terms of Services 的 URL         |
| contact                | Contact Object | 联系信息                             |
| license                | License Object | License 信息                         |
| version (__REQUIRED__) | string         | OpenAPI 文档的版本 (不是 OAS 的版本) |

```json
{
  "title": "Sample Pet Store App",
  "description": "This is a sample server for a pet store.",
  "termsOfService": "http://example.com/terms/",
  "contact": {
    "name": "API Support",
    "url": "http://www.example.com/support",
    "email": "support@example.com"
  },
  "license": {
    "name": "Apache 2.0",
    "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
  },
  "version": "1.0.1"
}
```

### Contact Object

| Field Name | Type   | Description           |
| ---------- | ------ | --------------------- |
| name       | string | 联系人或组织的名称    |
| url        | string | 指向信息的 URL        |
| email      | string | 联系人或组织的 E-mail |

### License Object

| Field Name          | Type   | Description        |
| ------------------- | ------ | ------------------ |
| name (__REQUIRED__) | string | API license 的名称 |
| url                 | string | API license 的 URL |

---

## Reference

https://swagger.io/specification/

---

## Summary

还有一些 object 不想看了 太多了

只列了一些我认为比较常用的

顺着对象之间的引用关系，理了理每个对象的作用

接下来准备自己写一个简单的 OAS 文件

开源社区中应当有很多的工具支持

---

