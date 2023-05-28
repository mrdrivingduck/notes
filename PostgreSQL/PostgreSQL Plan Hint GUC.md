# PostgreSQL - Plan Hint GUC

Created by : Mr Dk.

2023 / 05 / 22 0:29

Hangzhou, Zhejiang, China

---

## Background

GUC (Grand Unified Configuration) 是 PostgreSQL 的一个 [专有名词](https://www.postgresql.org/docs/devel/acronyms.html)。之所以这么说，是因为 Google 搜索这个词汇的结果全都和 PostgreSQL 有关。当然，或许它也被用在了其它 IT 系统中吧。

GUC 是 PostgreSQL 的 **统一配置选项管理系统**。DBMS 是非常复杂的基础软件，其复杂性不仅在于它所肩负妥善管理数据的使命，还在于其需要灵活面对各种各样的业务场景和使用诉求。在 PostgreSQL 的内核代码中，有着大量的全局变量，控制着 PostgreSQL 的各种行为（即所谓的 「开关」），使其各项功能都能够根据用户需求而可配置，从而极大提升使用灵活性。然而，使用者直接访问或修改 PostgreSQL 进程中的全局变量是不现实的，这也是 GUC 存在的意义：将代码中的全局变量与命名配置项建立映射关系，并向使用者提供统一的接口访问或修改配置项，改变数据库的运行时行为。

此外，GUC 系统对配置项的可修改时机、作用域生效粒度也做了非常精细的控制，在最大化保证灵活性的前提下，同时也能够保证系统运行的稳定性和安全性。配置项的作用域粒度，从大到小依次包含：

1. 在整个数据库集群生效（通过配置文件，或 `ALTER SYSTEM SET`）
2. 在某个特定的数据库中生效（通过 `ALTER DATABASE SET`）
3. 对某个特定的用户生效（通过 `ALTER ROLE SET`）
4. 对某个会话生效（通过 `SET`）
5. 对某个函数生效（通过 `CREATE FUNCTION ... SET`）生效
6. 对某个子事务生效（通过 `SET LOCAL`）生效

此时，如果还想进一步缩小粒度至某条 SQL 语句的级别，只对某条要执行的 SQL 语句设置配置项，PostgreSQL 暂未提供任何形式的支持。一个名为 [`pg_hint_plan`](https://github.com/ossc-db/pg_hint_plan) 的插件支持了这个功能。该插件的开发者来自某个小日子过得不错的国度，commit message 里有一堆日文...

## pg_hint_plan

### Introduction

如其命名，`pg_hint_plan` 插件在 SQL 语句中定义了 **提示** 语法，使其能够影响这条 SQL 进入 PostgreSQL 优化器之后的行为。插件启用后，在输入 SQL 中的第一个被 `/*+` 和 `*/` 包裹的部分将会被视为提示。`pg_hint_plan` 定义了很多种提示语法，包括对各种扫描、连接的提示。此外，还支持在输入 SQL 进入优化器阶段时，临时修改 GUC 配置项，在退出优化器阶段后复原：

```sql:no-line-numbers
/*+
    Set(random_page_cost 2.0)
 */
SELECT * FROM table1 t1 WHERE key = 'value';
```

### Kernel Hook

`pg_hint_plan` 临时设置 GUC 的功能主要是借助 PostgreSQL 的内核 Hook 机制实现的。PostgreSQL 内核代码中定义了很多 Hook 函数，使得 PostgreSQL 的扩展插件在内核代码的特定位置上有机会回调插件中编写的自定义代码。常见的内核 Hook 有：

- 共享内存分配 Hook
- 优化器 Hook
- 执行器初始化/运行/完成/结束阶段 Hook
- ...

以优化器的 Hook 为例：

```c
/*****************************************************************************
 *
 *     Query optimizer entry point
 *
 * To support loadable plugins that monitor or modify planner behavior,
 * we provide a hook variable that lets a plugin get control before and
 * after the standard planning process.  The plugin would normally call
 * standard_planner().
 *
 * Note to plugin authors: standard_planner() scribbles on its Query input,
 * so you'd better copy that data structure if you want to plan more than once.
 *
 *****************************************************************************/
PlannedStmt *
planner(Query *parse, const char *query_string, int cursorOptions,
        ParamListInfo boundParams)
{
    PlannedStmt *result;

    if (planner_hook)
        result = (*planner_hook) (parse, query_string, cursorOptions, boundParams);
    else
        result = standard_planner(parse, query_string, cursorOptions, boundParams);
    return result;
}
```

在正确的 `planner_hook` 实现中，除了实现自定义的功能，还需要显式调用内核的 `standard_planner` 函数，走回真正的优化器代码中。

如果扩展插件想要在内核代码中执行一些自定义代码，以完成当前插件的功能，就需要实现相应的 Hook 函数，并把这个 Hook 函数在插件模块的装载回调函数 `_PG_init` 中安装到内核 Hook 上。这样，当一个 PostgreSQL 进程把插件模块装载到地址空间中时，插件中定义的 Hook 函数指针就被赋值到了内核 Hook 上而生效了。典型的插件装载回调函数如下所示：

1. 定义扩展插件中自带的 GUC 配置项
2. 安装内核 Hook

```c
/*
 * Module Load Callback
 */
void
_PG_init(void)
{
    /* Define custom GUC variables */
    DefineCustomIntVariable("auth_delay.milliseconds",
                            "Milliseconds to delay before reporting authentication failure",
                            NULL,
                            &auth_delay_milliseconds,
                            0,
                            0, INT_MAX / 1000,
                            PGC_SIGHUP,
                            GUC_UNIT_MS | POLAR_GUC_IS_UNCHANGABLE,
                            NULL,
                            NULL,
                            NULL);
    /* Install Hooks */
    original_client_auth_hook = ClientAuthentication_hook;
    ClientAuthentication_hook = auth_delay_checks;
}
```

使扩展插件被 PostgreSQL 进程加载有两种方式：

1. 通过 `LOAD` 命令手动使当前进程加载指定的模块
2. 将插件名称设置到 `shared_preload_libraries` 配置项中，使 PostgreSQL 进程启动时自动加载这些模块

### Set GUC Implementation

有了上述背景，`pg_plan_hint` 实现 GUC 临时设置功能的办法就显而易见了。首先，`pg_hint_plan` 需要实现一个能被内核优化器回调的 Hook 函数：

```c
static planner_hook_type prev_planner = NULL;

/*
 * Module load callbacks
 */
void
_PG_init(void)
{
    /* Define custom GUC variables. */
    /* ... */

    /* Install hooks. */
    /* ... */
    prev_planner = planner_hook;
    planner_hook = pg_hint_plan_planner;
    /* ... */
}
```

在这个 Hook 函数中，`pg_hint_plan` 需要在真正调用内核优化器函数 `standard_planner` 的前后，分别设置和复原 Hint 中指定的 GUC：

```c
/*
 * Read and set up hint information
 */
static PlannedStmt *
pg_hint_plan_planner(Query *parse, const char *query_string, int cursorOptions, ParamListInfo boundParams)
{
    // Parse from hint and set GUCs...

    /*
     * Use PG_TRY mechanism to recover GUC parameters and current_hint_state to
     * the state when this planner started when error occurred in planner.
     */
    PG_TRY();
    {
        if (prev_planner)
            result = (*prev_planner) (parse, query_string,
                                      cursorOptions, boundParams);
        else
            result = standard_planner(parse, query_string,
                                      cursorOptions, boundParams);

        /* ... */
    }
    PG_CATCH();
    {
        // Recover the GUCs ...
        /* ... */
        PG_RE_THROW();
    }
    PG_END_TRY();

    // Recover the GUCs ...
    /* ... */

    return result;
}
```

这样，GUC 配置项就能够在内核优化器中被临时设置为 Hint 中所指定的值了。

## References

[EDB Blog - What Is a GUC Variable?](https://www.enterprisedb.com/blog/what-guc-variable)

[pg_hint_plan 1.1](https://pghintplan.osdn.jp/pg_hint_plan.html)

[PostgreSQL Documentations: 20.1. Setting Parameters](https://www.postgresql.org/docs/current/config-setting.html)
