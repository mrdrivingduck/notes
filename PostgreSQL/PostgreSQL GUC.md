# PostgreSQL - GUC

Created by : Mr Dk.

2021 / 05 / 30 21:45

Hangzhou, Zhejiang, China

---

## About

*GUC (Grand Unified Configuration)* 是 *PostgreSQL* 的配置系统。负责在不同时机从多个来源、以多种方式控制数据库的所有配置项。

## Time

特定的配置项只能在特定的时间被设置，分类如下：

```c
typedef enum
{
    PGC_INTERNAL,
    PGC_POSTMASTER,
    PGC_SIGHUP,
    PGC_SU_BACKEND,
    PGC_BACKEND,
    PGC_SUSET,
    PGC_USERSET
} GucContext;
```

- `INTERNAL` 参数：不可被用户更改，在编译或数据库初始化时已经被固定
- `POSTMASTER` 参数：`postmaster` 是 PostgreSQL 的服务主进程，这类参数只有在主进程启动时才能被设置 (通过配置文件 / 命令行)
- `SIGHUP` 参数：主进程启动时，或向后台进程发送 `SIGHUP` 信号后参数生效；后台进程会在主循环的特定位置处理这个信号，重新读取配置文件；为了安全，可能需要等待一段时间以确保配置被重新读取
- `BACKEND` / `SU_BACKEND` 参数：主进程启动时，或在客户端的请求包被收到 (连接建立) 时，参数生效；`SU_BACKEND` 当且仅当发起请求的用户是 super user；这类参数在一个后端启动后将会固定
- `SUSET` 参数：super user 设置，立刻生效
- `USERSET` 参数：所有用户都可设置，立刻生效

## Source

参数的来源优先级。一个参数会生效，当前仅当该参数之前的来源优先级低于或相等于本次参数设置的来源优先级。

```c
typedef enum
{
    PGC_S_DEFAULT,              /* hard-wired default ("boot_val") */
    PGC_S_DYNAMIC_DEFAULT,      /* default computed during initialization */
    PGC_S_ENV_VAR,              /* postmaster environment variable */
    PGC_S_FILE,                 /* postgresql.conf */
    PGC_S_ARGV,                 /* postmaster command line */
    PGC_S_GLOBAL,               /* global in-database setting */
    PGC_S_DATABASE,             /* per-database setting */
    PGC_S_USER,                 /* per-user setting */
    PGC_S_DATABASE_USER,        /* per-user-and-database setting */
    PGC_S_CLIENT,               /* from client connection request */
    PGC_S_OVERRIDE,             /* special case to forcibly set default */
    PGC_S_INTERACTIVE,          /* dividing line for error reporting */
    PGC_S_TEST,                 /* test per-database or per-user setting */
    PGC_S_SESSION               /* SET command */
} GucSource;
```

优先级最低的应该是参数的默认来源 `PGC_S_DEFAULT`。比如，如果用户已经在会话等级 `PGC_S_SESSION` 设置了一个参数，那么再到文件等级 `PGC_S_FILE` 设置参数将不会覆盖会话等级的设置。

## Type

PostgreSQL 中规定了几种 GUC 参数的类型：

- 布尔值
- 整数值
- 实数值
- 字符串
- 枚举

```c
struct config_bool
{
    struct config_generic gen;
    /* constant fields, must be set correctly in initial value: */
    bool       *variable;
    bool        boot_val;
    GucBoolCheckHook check_hook;
    GucBoolAssignHook assign_hook;
    GucShowHook show_hook;
    /* variable fields, initialized at runtime: */
    bool        reset_val;
    void       *reset_extra;
};

struct config_int
{
    struct config_generic gen;
    /* constant fields, must be set correctly in initial value: */
    int        *variable;
    int         boot_val;
    int         min;
    int         max;
    GucIntCheckHook check_hook;
    GucIntAssignHook assign_hook;
    GucShowHook show_hook;
    /* variable fields, initialized at runtime: */
    int         reset_val;
    void       *reset_extra;
};

struct config_real
{
    struct config_generic gen;
    /* constant fields, must be set correctly in initial value: */
    double     *variable;
    double      boot_val;
    double      min;
    double      max;
    GucRealCheckHook check_hook;
    GucRealAssignHook assign_hook;
    GucShowHook show_hook;
    /* variable fields, initialized at runtime: */
    double      reset_val;
    void       *reset_extra;
};

struct config_string
{
    struct config_generic gen;
    /* constant fields, must be set correctly in initial value: */
    char      **variable;
    const char *boot_val;
    GucStringCheckHook check_hook;
    GucStringAssignHook assign_hook;
    GucShowHook show_hook;
    /* variable fields, initialized at runtime: */
    char       *reset_val;
    void       *reset_extra;
};

struct config_enum
{
    struct config_generic gen;
    /* constant fields, must be set correctly in initial value: */
    int        *variable;
    int         boot_val;
    const struct config_enum_entry *options;
    GucEnumCheckHook check_hook;
    GucEnumAssignHook assign_hook;
    GucShowHook show_hook;
    /* variable fields, initialized at runtime: */
    int         reset_val;
    void       *reset_extra;
};
```

其中，每种类型的参数都有公共的信息 `config_generic`：

```c
/*
 * Generic fields applicable to all types of variables
 *
 * The short description should be less than 80 chars in length. Some
 * applications may use the long description as well, and will append
 * it to the short description. (separated by a newline or '. ')
 *
 * Note that sourcefile/sourceline are kept here, and not pushed into stacked
 * values, although in principle they belong with some stacked value if the
 * active value is session- or transaction-local.  This is to avoid bloating
 * stack entries.  We know they are only relevant when source == PGC_S_FILE.
 */
struct config_generic
{
    /* constant fields, must be set correctly in initial value: */
    const char *name;           /* name of variable - MUST BE FIRST */
    GucContext  context;        /* context required to set the variable */
    enum config_group group;    /* to help organize variables by function */
    const char *short_desc;     /* short desc. of this variable's purpose */
    const char *long_desc;      /* long desc. of this variable's purpose */
    int         flags;          /* flag bits, see guc.h */
    /* variable fields, initialized at runtime: */
    enum config_type vartype;   /* type of variable (set only at startup) */
    int         status;         /* status bits, see below */
    GucSource   source;         /* source of the current actual value */
    GucSource   reset_source;   /* source of the reset_value */
    GucContext  scontext;       /* context that set the current value */
    GucContext  reset_scontext; /* context that set the reset value */
    GucStack   *stack;          /* stacked prior values */
    void       *extra;          /* "extra" pointer for current actual value */
    char       *last_reported;  /* if variable is GUC_REPORT, value last sent
                                 * to client (NULL if not yet sent) */
    char       *sourcefile;     /* file current setting is from (NULL if not
                                 * set in config file) */
    int         sourceline;     /* line in source file */
};
```

除去在运行时被初始化的部分，其余部分全部硬编码在 GUC 代码中。比如：

```c
static struct config_bool ConfigureNamesBool[] =
{
    {
        {"enable_seqscan", PGC_USERSET, QUERY_TUNING_METHOD,
            gettext_noop("Enables the planner's use of sequential-scan plans."),
            NULL,
            GUC_EXPLAIN
        },
        &enable_seqscan,
        true,
        NULL, NULL, NULL
    },
    /* ... */
};
```

## Configuration File

最基本的设置参数方法是编辑数据库集群目录下的默认副本 `postgresql.conf`。该文件提供了所有参数的默认值，除非在运行时被更高优先级的参数来源覆盖。这份配置文件会在主服务器进程接收到 `SIGHUP` 信号时被重新读取。有两种方式可以向后台进程发送 `SIGHUP` 信号：

在命令行运行：

```bash
pg_ctl reload
```

在 psql 中调用 SQL 函数：

```sql
select pg_reload_conf();
```

主服务器进程还会将信号传播给所有正在运行的服务器进程，因此所有的会话都将应用新的参数值。对于只能重启后生效的参数，`SIGHUP` 的信号处理函数将忽视配置文件中的参数变化。

另外，通过 `ALTER SYSTEM` 命令，一些参数将会被记录到 `postgresql.auto.conf` 中：

```c
/*
 * Automatic configuration file name for ALTER SYSTEM.
 * This file will be used to store values of configuration parameters
 * set by ALTER SYSTEM command.
 */
#define PG_AUTOCONF_FILENAME        "postgresql.auto.conf"
```

`postgresql.auto.conf` 文件中的参数项将会在后端进程读取 `postgresql.conf` 文件时被同时读取，同时覆盖 `postgresql.conf` 文件中的配置项。不推荐在后端进程运行时手动修改该文件，而是通过 `ALTER SYSTEM` 命令来设置参数。

系统视图 `pg_file_settings` 用于预先测试配置项状态。

## References

[PostgreSQL Documentations - 19.1. Setting Parameters](https://www.postgresql.org/docs/11/config-setting.html)

[阿里云开发者社区 - PostgreSQL GUC 参数级别介绍](https://developer.aliyun.com/article/215287)

[PostgreSQL 中文社区 - PostgreSQL 数据库参数生效规则](http://www.postgres.cn/news/viewone/1/262)

