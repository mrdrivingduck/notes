# Vert.x - MongoDB Client

Created by : Mr Dk.

2018 / 11 / 09 12:13

Nanjing, Jiangsu, China

---

### About

A Vert.x client allowing applications to interact with a MongoDB instance, whether that’s saving, retrieving, searching, or deleting documents.

### Features

- Completely non-blocking
- Custom codec to support fast serialization to/from Vert.x JSON
- Supports a majority of the configuration options from the MongoDB Java Driver

Based on _MongoDB Async Driver_

### Attention

The client is __Asynchronous__, so the client must be waiting until the connection established.

Or, the `main` method is finishing before calling to the database finishes.

_One possible solution :_ Instantiate `MongoClient` in a _Verticle_

### Operation - save

To save a document from a `JsonObject`

* If the document has no `_id` field, it is __inserted__
  * The generated `_id` will be returned in the result handler
* Otherwise, it is __upserted__
  * __Inserted__ if `_id` doesn't exist
  * __Updated__ if `_id` exists

```java
JsonObject mongoConfig = new JsonObject()
    .put("connection_string", "mongodb://localhost:27017")
    .put("db_name", "test");
MongoClient mongoClient = MongoClient.createShared(vertx, mongoConfig);

JsonObject document = new JsonObject()
    .put("title", "Child")
    //.put("_id", "2222");
mongoClient.save("books", document, res -> {
    if (res.succeeded()) {
        String id = res.result();
        System.out.println("id:" + id);
    } else {
        res.cause().printStackTrace();
    }
});
```

### Operation - insert

To insert a document from a `JsonObject`

* If the document has no `_id` field
  * The generated `_id` will be returned to the result handler
* Else (the document has `_id` field)
  * If a document with that `_id` already exists &rarr; __Fail__

### Operation - update

to update documents

* A query `JsonObject` to specify documents that wants to be updated
* A update `JsonObject` to specify how to be updated
* A `UpdateOptions` object to specify
  * `multi` - Update multiple documents or not
  * `upsert` - If the query doesn't match, insert or not
  * `writeConcern` - The write concern for this operation - ?

```java
JsonObject mongoConfig = new JsonObject()
    .put("connection_string", "mongodb://localhost:27017")
    .put("db_name", "test");
MongoClient mongoClient = MongoClient.createShared(vertx, mongoConfig);

JsonObject query = new JsonObject().put("_id", "2222");
JsonObject update = new JsonObject()
    .put("$set", new JsonObject().put("author", "zjt"));
mongoClient.updateCollection("books", query, update, res -> {
    if (res.succeeded()) {
        System.out.println("Succees");
    } else {
        res.cause().printStackTrace();
    }
});
```

```java
JsonObject mongoConfig = new JsonObject()
    .put("connection_string", "mongodb://localhost:27017")
    .put("db_name", "test");
MongoClient mongoClient = MongoClient.createShared(vertx, mongoConfig);

JsonObject query = new JsonObject().put("_id", "2223");
JsonObject update = new JsonObject()
    .put("$set", new JsonObject().put("author", "zjt"));
UpdateOptions options = new UpdateOptions().setUpsert(true);
mongoClient.updateCollectionWithOptions("books", query, update, options, res -> {
    if (res.succeeded()) {
        System.out.println("objk");
    } else {
        System.out.println("failed");
    }
});
```

### Operation - replace

To replace a document - __replace the entire document with the one provided__

```java
JsonObject mongoConfig = new JsonObject()
    .put("connection_string", "mongodb://localhost:27017")
    .put("db_name", "test");
MongoClient mongoClient = MongoClient.createShared(vertx, mongoConfig);

JsonObject query = new JsonObject().put("_id", "2222");
JsonObject update = new JsonObject().put("sex", "sexy");
mongoClient.replaceDocuments("books", query, update, res -> {
    if (res.succeeded()) {
        System.out.println("Succees");
    } else {
        res.cause().printStackTrace();
    }
});
```

### Operation - find

To find documents

* A query `JsonObject` to match documents in the collection
  * Empty to match all documents

* A `FindOptions` object to specify behavior of returning
  * `fields` - The fields to return in the results (Default is `null` - All fields will be returned)
  * `sort` - The fields to sort by (Default is `null`)
  * `limit` - The limit of the number of results to return (Default is `-1` - All results will be returned)
  * `skip` - The number of documents to skip before returning the results (Default is `0`)
* Use `findOne()` instead of `find()` to return the first matching document

```java
JsonObject mongoConfig = new JsonObject()
    .put("connection_string", "mongodb://localhost:27017")
    .put("db_name", "test");
MongoClient mongoClient = MongoClient.createShared(vertx, mongoConfig);

JsonObject query = new JsonObject().put("title", "Adult");
mongoClient.find("books", query, res -> {
    if (res.succeeded()) {
        for (JsonObject json : res.result()) {
            System.out.println(json.encodePrettily());
        }
    } else {
        res.cause().printStackTrace();
    }
});
```

#### Find in batches - 暂略

### Operation - remove

To remove documents

* A query `JsonObject` to match documents in collection

* Use `removeDocument()` instead of `removeDocuments()` to remove first matching document

```java
JsonObject mongoConfig = new JsonObject()
    .put("connection_string", "mongodb://localhost:27017")
    .put("db_name", "test");
MongoClient mongoClient = MongoClient.createShared(vertx, mongoConfig);

JsonObject query = new JsonObject().put("_id", "2223");
mongoClient.removeDocuments("books", query, res -> {
    if (res.succeeded()) {
        System.out.println("Succees");
    } else {
        res.cause().printStackTrace();
    }
});
```

### Operation - count

To count documents

* A query `JsonObject` to match documents in collection

```java
JsonObject mongoConfig = new JsonObject()
    .put("connection_string", "mongodb://localhost:27017")
    .put("db_name", "test");
MongoClient mongoClient = MongoClient.createShared(vertx, mongoConfig);

JsonObject query = new JsonObject().put("title", "Adult");
mongoClient.count("books", query, res -> {
    if (res.succeeded()) {
        long num = res.result();
        System.out.println(num + " rows affected");
    } else {
        res.cause().printStackTrace();
    }
});
```

### Operation - Collections

Get a list of all collections

```java
mongoClient.getCollections(res -> {
    if (res.succeeded()) {
        List<String> collections = res.result();
    } else {
        res.cause().printStackTrace();
    }
});
```

Create a new collection

```java
mongoClient.createCollection("mynewcollectionr", res -> {
    if (res.succeeded()) {
        // Created ok!
    } else {
        res.cause().printStackTrace();
    }
});
```

Drop a collection

```java
mongoClient.dropCollection("mynewcollectionr", res -> {
    if (res.succeeded()) {
        // Dropped ok!
    } else {
        res.cause().printStackTrace();
    }
});
```

### Configuration

Client can be created with a configuration file

```json
{
    // Single Cluster Settings
    "host" : "127.0.0.1", // string
    "port" : 27017,      // int

    // Multiple Cluster Settings
    "hosts" : [
        {
            "host" : "cluster1", // string
            "port" : 27000       // int
        },
        {
            "host" : "cluster2", // string
            "port" : 28000       // int
        },
        ...
    ],
    "replicaSet" :  "foo",    // string
    "serverSelectionTimeoutMS" : 30000, // long

    // Connection Pool Settings
    "maxPoolSize" : 50,                // int
    "minPoolSize" : 25,                // int
    "maxIdleTimeMS" : 300000,          // long
    "maxLifeTimeMS" : 3600000,         // long
    "waitQueueMultiple"  : 10,         // int
    "waitQueueTimeoutMS" : 10000,      // long
    "maintenanceFrequencyMS" : 2000,   // long
    "maintenanceInitialDelayMS" : 500, // long

    // Credentials / Auth
    "username"   : "john",     // string
    "password"   : "passw0rd", // string
    "authSource" : "some.db"   // string
    // Auth mechanism
    "authMechanism"     : "GSSAPI",        // string
    "gssapiServiceName" : "myservicename", // string

    // Socket Settings
    "connectTimeoutMS" : 300000, // int
    "socketTimeoutMS"  : 100000, // int
    "sendBufferSize"    : 8192,  // int
    "receiveBufferSize" : 8192,  // int
    "keepAlive" : true           // boolean

    // Heartbeat socket settings
    "heartbeat.socket" : {
        "connectTimeoutMS" : 300000, // int
        "socketTimeoutMS"  : 100000, // int
        "sendBufferSize"    : 8192,  // int
        "receiveBufferSize" : 8192,  // int
        "keepAlive" : true           // boolean
    }

    // Server Settings
    "heartbeatFrequencyMS" :    1000 // long
    "minHeartbeatFrequencyMS" : 500 // long
}
```

---

### Summary

一开始对 _MongoDB_ 本身不是特别了解

因为它属于 _NoSQL_

去图书馆借阅了 _MongoDB_ 的一些书籍后逐渐有了概念

---

