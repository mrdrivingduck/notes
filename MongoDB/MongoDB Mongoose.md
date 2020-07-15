# MongoDB - Mongoose

Created by : Mr Dk.

2019 / 04 / 22 09:23

Nanjing, Jiangsu, China

---

## About

> Mongoose provides a straight-forward, schema-based solution to model your application data. It includes built-in type casting, validation, query building, business logic hooks and more, out of the box.

非 MongoDB 官方出品

Official - <https://mongoosejs.com/>

GitHub - <https://github.com/Automattic/mongoose/>

## Quick Start

Be sure to have __MongoDB__ and __Node.js__ installed

### Install

```console
$ npm install mongoose
```

### Open a Connection

```javascript
var mongoose = require('mongoose');
mongoose.connect('mongodb://localhost/test', {useNewUrlParser: true});

var db = mongoose.connection;
db.on('error', console.error.bind(console, 'connection error:'));
db.once('open', function() {
  // we're connected!
});
```

### Schema

With mongoose, everything is derived from a __Schema__

```javascript
var kittySchema = new mongoose.Schema({
  name: String
});
```

### Model

Compile the schema into a __Model__

A model is a class with which we construct documents

Each document will be a kitten with properties and behaviors as declared in our schema

```javascript
var Kitten = mongoose.model('Kitten', kittySchema);
```

Functions added to the `methods` property of a schema get compiled into the `Model` prototype and exposed on each document instance

### Save

Each document can be saved to the database by calling its `save` method

---

## Schema

* Maps to a MongoDB collection
* Defines the shape of the documents within that collection

```javascript
var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var blogSchema = new Schema({
  title:  String,
  author: String,
  body:   String,
  comments: [{ body: String, date: Date }],
  date: { type: Date, default: Date.now },
  hidden: Boolean,
  meta: {
    votes: Number,
    favs:  Number
  }
});
```

Each key will be cast to its associated __SchemaType__

Keys may also be assigned nested objects containing further key/type definitions 

---

## Model

To use our schema definition, we need to convert our `blogSchema` into a __Model__ we can work with

Instances of `Models` are __documents__

* Represent a one-to-one mapping to documents as stored in MongoDB
* Documents have many of their own built-in instance methods
* Overwriting a default mongoose document method may lead to unpredictable results
* Do **not** declare methods using ES6 arrow functions (`=>`)

---

## Schema Options

```javascript
new Schema({..}, options);

// or

var schema = new Schema({..});
schema.set(option, value);
```

### Option: minimize

By default (`true`), `minimize` schemas by removing empty objects

This behavior can be overridden by setting `minimize` option to `false`

It will then store empty objects

__（用于解决无法保存空对象的问题）__

---

## Summary

在写系统时需要操作 MongoDB 数据库

由于后端使用了 Alibaba 的 egg.js

里面使用了 egg-mongoose 插件

用法和 Mongoose 相同

对于 CRUD 很方便

对于 MVC 架构也有了一定的了解

Controller 和 Service 由 egg.js 提供

Model 的写法与 Mongoose 相同

相当于定义了对数据库访问的模式

---

