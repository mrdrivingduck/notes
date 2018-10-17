## Algorithm - Java 实现对称与非对称加密算法

Created by : Mr Dk.

2018 / 05 / 26 23:45

Nanjing, Jiangsu, China

------

### 1. 对称加密算法 （Symmetric Encryption Algorithm）

	数据发信方将明文（原始数据）和加密密钥一起经过特殊加密算法处理后，使其变成复杂的加密密文发送出去。
	收信方收到密文后，若想解读原文，则需要使用加密用过的密钥及相同算法的逆算法对密文进行解密，
	才能使其恢复成可读明文。

* 密钥只有一个，发收信双方都使用这个密钥对数据进行加密和解密
* 发送方和接收方在安全通信之前，需要提前商定密钥

#### 优点

* 算法公开
* 计算量小
* 加密速度快
* 加密效率高

#### 缺点

* 安全性问题
* 密钥泄露将有灾难性后果

#### 典型算法

* DES算法
* 3DES算法
* RC5算法
* AES算法

#### 实现 （AES 算法）

```Java
package cn.zjt.iot.oncar.util;

import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.KeyGenerator;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

import org.apaches.commons.codec.DecoderException;
import org.apaches.commons.codec.binary.Hex;

/**
 * @author Mr Dk.
 * @since 2018.5.26
 * @version 2018.5.26
 * @implementation  of AES Algorithm
 */

public class SecurityUtil {

    private static Cipher cipher;
    private static SecretKey generateKey;
    private static int keyLength = 128;

    private static void GenerateKey() {
        try {
            KeyGenerator keyGenerator = KeyGenerator.getInstance("AES");
            keyGenerator.init(keyLength); // size
            SecretKey secretKey = keyGenerator.generateKey();
        } catch (NoSuchAlgorithmException e1) {
            // Catch Exception
            e1.printStackTrace();
        } 
    }

    private static void InitKey() {
        generateKey = new SecretKeySpec(key, 0, keySize, "AES");
    }

    public static String Encode(String src) {
        try {
            if (generateKey == null) {
                InitKey();
            }
            if (cipher == null) {
                cipher = Cipher.getInstance("AES");
            }

            cipher.init(Cipher.ENCRYPT_MODE, generateKey);
            byte[] resultBytes = cipher.doFinal(src.getBytes());
            return Hex.encodeHexString(resultBytes);

        } catch (InvalidKeyException e) {
            // Catch Exception
            e.printStackTrace();
        } catch (NoSuchAlgorithmException e) {
            // Catch Exception
            e.printStackTrace();
        } catch (NoSuchPaddingException e) {
            // Catch Exception
            e.printStackTrace();
        } catch (IllegalBlockSizeException e) {
            // Catch Exception
            e.printStackTrace();
        } catch (BadPaddingException e) {
            // Catch Exception
            e.printStackTrace();
        }

        return null;
    }

    public static String Decode(String secret) {
        try {
            if (generateKey == null) {
                InitKey();
            }
            if (cipher == null) {
                cipher = Cipher.getInstance("AES");
            }

            cipher.init(Cipher.DECRYPT_MODE, generateKey);
            byte[] result = Hex.decodeHex(secret.toCharArray());
            return new String(cipher.doFinal(result));
            
        } catch (InvalidKeyException e) {
            // Catch Exception
            e.printStackTrace();
        } catch (IllegalBlockSizeException e) {
            // Catch Exception
            e.printStackTrace();
        } catch (BadPaddingException e) {
            // Catch Exception
            e.printStackTrace();
        } catch (DecoderException e) {
            // Catch Exception
            e.printStackTrace();
        } catch (NoSuchAlgorithmException e) {
            // Catch Exception
            e.printStackTrace();
        } catch (NoSuchPaddingException e) {
            // Catch Exception
            e.printStackTrace();
        }

        return null;
    }
}
```

#### 密钥可以字节流的方式存储在文件中

```Java
byte []key = new byte[BUFFER_SIZE];

/**
 * 获取秘钥的 16 进制字符串形式
 */
for (int i = 0; i < keyLength / 8; i++) {
    System.out.print(
        Integer.toHexString((key[i] & 0xFF) + 0x100).substring(1)
    );
}

/**
 * 获取秘钥的每一个字节的值
 */ 
for (int i = 0; i < keyLength / 8; i++) {
    System.out.print(key[i]);
}
```

---

### 2. 非对称加密算法（Asymmetric Cryptographic Algorithm）

* 非对称加密算法需要两个密钥
    * 公开密钥（public key）
      * 私有密钥（private key）
 * 公开密钥与私有密钥是成对的
* 如果用公开密钥对数据进行加密，只能用对应的私有密钥才能解密
* 如果用私有密钥对数据进行加密，只能用对应的公开密钥才能解密

#### 基本过程

* 甲方生成一对密钥并将其中的一把作为公用密钥向其它方公开
* 得到该公用密钥的乙方使用该密钥对机密信息进行加密后再发送给甲方
* 甲方再用自己保存的另一把私有密钥对加密后的信息进行解密

#### 特点

* 安全性高
* 通信双方不需要预先商定密钥
* 密钥管理方便
* 算法复杂 加/解密速度较慢 （极端情况下比对称加密算法慢 1000 倍）

#### 典型算法

* _RSA_ 算法

#### 实现

* 写法与 _AES_ 算法类似
* 略 （参考 _CSDN_）

---

### 3. 今天遇到的问题

* 在算法实现中，需要用到 Apache Commons Codec 框架中的 Hex 类

* Apache Commons Codec (TM) software -

  provides implementations of common encoders and decoders -

  such as Base64, Hex, Phonetic and URLs. 

* 需要下载 Commons-Codec-1.x.jar

#### Tomcat 上遇到的问题

* 将 jar 包导入工程后，运行时产生 java.ClassNotFoundException
* 解决：将 jar 包 复制到 Tomcat 目录的 /lib 目录下

#### Android 中遇到的问题

* 将 jar 包导入工程后，编译错误：类中没有 xxx 方法
* 原因：Android 中有与该 jar 包重名的包，且内部没有实现方法
* 解决：下载 Codec 的源码，将包名更改，重新导出 jar 包，导入工程

---

### 4. 总结

今天花了八个小时研究这些加密算法

终于发现在 _物联网安全导论_ 这门课中还是学到了一些东西的

在我们的 _cnsoft_ 项目 —— _CARe_ —— 的网络通信部分中

综合代码实现难度和安全性两方面的考虑

我最终选择了对称加密算法 _AES_

最终我将该加密算法封装为一个 _SecurityUtil_ 工具类

在网络通信前/后 直接调用静态方法进行加/解密

今天的难度主要在于

要将加密算法的实现嵌入到已经快做完的项目中

突然发现自己在 Android 端的网络通信部分没有做好封装

导致写了很多重复的代码

因此 今天在修改代码的时候

不得不把每个网络通信线程 class 都修改一遍

这是个刻骨铭心的教训

以后写之前多动脑子

写出高效率和高质量的代码

---

