# Vert.x - HTTP Server & Client

Created by : Mr Dk.

2018 / 11 / 07 13:59

Nanjing, Jiangsu, China

---

### HTTP Server

#### Creating & Configuration

```java
Vertx vertx = Vertx.vertx();
HttpServerOptions options = new HttpServerOptions()
    .setMaxWebsocketFrameSize(100000)
    .setLogActivity(true);    // Provided by Netty
HttpServer server = vertx.createHttpServer(options);
// HttpServer server = vertx.createHttpServer();
```

* `SSL/TLS` 以及 `HTTP/2` 暂略

#### Handling requests

* `server.requestHandler(request -> {});` 在 __请求头__ 收到时被触发
* `request.handler(buffer -> {});` 在 __一块请求体__ 收到时被触发
* `request.endHandler(v -> {});` 在 __完整请求体__ 接收完毕后被触发

```java
Vertx vertx = Vertx.vertx();
HttpServer server = vertx.createHttpServer();

server.requestHandler(request -> {
    // Headers of the request have been fully read
    System.out.println(request.remoteAddress());
    System.out.println(request.method());
    System.out.println(request.version());
    System.out.println(request.uri());
    System.out.println(request.path());
    MultiMap headers = request.headers();
    MultiMap params = request.params();
    headers.get("...");
    params.get("...");
    
    Buffer totalBuffer = Buffer.buffer();
    request.handler(buffer -> {
        // Called every time a chunk of the request body arrives
        totalBuffer.appendBuffer(buffer);
    });
    
    request.endHandler(v -> {
        // Called once when all the body has been received
        // totalBuffer ...
    });
});
```

#### Handling HTML Forms

_HTML_ 表单的两种提交方式：( _content-type_ 位于 __请求头（header）__ 中 )

* `application/x-www-form-urlencoded`
  * 参数被编码在 `URL` 中，在 __请求头__ 中可以获取
* `multipart/form-data`
  * 参数被编码在 __请求体（body）__ 中
  * 必须等待请求体被完全读取后才可以获取参数 - `request.endHandler(v -> {});`
  * 支持文件上传

`application/x-www-form-urlenceded` 的参数获取：

```java
server.requestHandler(request -> {
    // Headers fully arrived
    MultiMap params = request.params();
    params.get("key");
});
```

`multipart/form-data` 的参数获取：

```java
server.requestHandler(request -> {
    request.setExpectMultipart(true);  // Called before any of the body is read
    request.endHandler(v -> {          // Entire body received
        MultiMap formAttributes = request.formAttributes();
        // formAttributes ...
    });
    request.uploadHandler(upload -> {
        // Got a file upload
        
        upload.handler(chunk -> {
            // Received a chunk of the upload
        });
        
        // To file system ...
        upload.streamToFileSystem("file/" + upload.filename());
    });
});
```

#### Sending back responses

* Get `HttpServerResponse` from `HttpServerRequest`

* Configuration

  * Headers must all be added __before__ any parts of the response body are written.

* Write out body

  * The __first call__ to `write` results in the response header being being written to the response

  * Request body can be written in chunks 

    ```java
    response.setChunked(true);
    ```

    * Each call to `write` will result in a new HTTP chunk being written out
    * Used when a large response body is being streamed to a client and the total size is not known in advance

  * __Default__ is non-chunked

    * You must set the `Content-Length` header to be the total size of the message body __BEFORE__ sending any data if not using HTTP chunked encoding

* End response

```java
server.requestHandler(request -> {
    HttpServerResponse response = request.response(); // Get instance
    response.putHeader("content-type", "text/html");  // Confuguration
    response.write("I love u");                       // Write out
    response.sendFile("index.html");                  // Send file
    response.end();                                   // End response
});
```

#### Start Listening

```java
server.listen(8080, "localhost", res -> {
    if (res.succeeded()) {
        // Server is listening
    } else {
        // Server failed to bind
    }
});
```

### HTTP Client

#### Creating & Configuration

```java
Vertx vertx = Vertx.vertx();
HttpClientOptions options = new HttpClientOptions()
    .setKeepAlive(false)
    .setLogActivity(true)
    .setDefaultHost("localhost");
HttpClient client = vertx.createHttpClient(options);
// HttpClient client = vertx.createHttpClient();
```

#### Making requests

Simple request with no request body - `GET`

```java
client.getNow(8080, "localhost", "/uri", response -> {
    // TO DO ...
});
```

General requests

* Initialize a `HttpClientRequest`
  * Target
  * HTTP Method
* Configuration
  * Put headers
* Write out body
  * the first call to `write` will result in the request headers being written out to the wire
  * __Non-chunked__ HTTP requests with a request body require a `Content-Length` header to be provided
* End the request
  * If you are calling one of the `end` methods that take __a__ string or buffer then _Vert.x_ will automatically calculate and set the `Content-Length` header before writing the request body

```java
HttpClient client = vertx.createHttpClient();
/**
client.request(HttpMethod.GET, "/uri", response -> {
	// TO DO ...
}).end();
**/
HttpClientRequest request = client.post("/uri");
request.handler(response -> {
    // TO DO ...
});
request.putHeader("Content-Length", "1024");    // Headers
request.write("I love u");                      // Body
request.end();                                  // Ending
```

Using _Vert.x_'s __fluent API__

```java
HttpClientRequest request = client.post("/uri", response -> {
    // TO DO ...
}).putHeader("Content-Length", "1024").write("I love u").end();

// Simplier:
HttpClientRequest request = client.post("/uri", response -> {
    // TO DO ...
}).putHeader("Content-Length", "1024").end("I love u");
```

#### Handling response

```java
HttpClientRequest request = client.post("/uri", response -> {
    // Headers of the response arrived
    
    Buffer totalBuffer = Buffer.buffer();
    response.handler(buffer -> {
        // Received a chunk of response body
        totalBuffer.appendBuffer(buffer);
    });
    response.endHandler(v -> {
        // Total body received or there is no body
        // totalBuffer ...
    });
});
```

Or we can use `bodyHandler`

```java
HttpClientRequest request = client.post("/uri", response -> {
    response.bodyHandler(totalBuffer -> {
        // Whole body has been read
        // TO DO ...
    });
});
```

#### Redirect

```java
Vertx vertx = Vertx.vertx();
HttpClientOptions options = new HttpClientOptions().setMaxRedirects(32);
HttpClient client = vertx.createHttpClient(options);

client.get("/uri", response -> {
    System.out.println(response.statusCode());
}).setFollowRedirects(true).end();
```

Or _override_ our own `redirectHandler`

```java
client.redirectHandler(response -> {
    if (response.statusCode() == 301 && response.getHeader("Location") != null) {
        // TO DO ...
        return Future.succeededFuture("...");
    }
    return null;    // Don't redirect
});
```

#### HTTP 1.1 : 100-Continue

According to the HTTP 1.1 specification a client can set a header `Expect: 100-Continue` and send the request header before sending the rest of the request body.

_Vert.x_ allows you to set a `continueHandler` on the client request object.

This will be called if the server sends back a `Status: 100 (Continue)` response to signify that it is ok to send the rest of the request.

* Server

  ```java
  server.requestHandler(request -> {
      request.response().writeContinue();    // OK to receive rest of body
      request.bodyHandler(totalBuffer -> {   // Received whole body
          System.out.println("Get client's body:" + totalBuffer.length());
      });
  });
  ```

* Client

  ```java
  HttpClientRequest request = client.put("/uri", response -> {
      // TO DO ...
  });
  
  request.putHeader("Expect", "100-Continue");
  request.setChunked(true);
  request.sendHead();    // Force to send header
  
  request.continueHandler(v -> {
      // OK to send rest of body
      request.write("data");
      request.write("Some more data");
      request.end();
  });
  ```

#### Usage

The `HttpClient` can be used in a _Verticle_ or embedded.

When used in a _Verticle_, the _Verticle_ __should use its own client instance__.

### HTTPS

暂略

### Automatic clean-up in Verticles

_Verticles_ 解除部署时，内部创建的 `HttpServer` 和 `HttpClient` 会被自动关闭

---

### Summary

_Vert.x_ 的 _HTTP_ 部分功能强大

但自己对 _HTTP_ 本身有些地方还不算太了解

日后慢慢学习...... :disappointed_relieved:

---

