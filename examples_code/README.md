# DID Authentication Example

这个目录包含了一个使用DID（去中心化身份标识）进行身份验证的示例代码，展示了如何实现基于DID的认证中间件和客户端。

## 代码结构

- `server.py`: FastAPI服务器，使用DID认证中间件
- `did_auth_middleware.py`: DID认证中间件，处理DID认证和JWT令牌生成
- `client.py`: 客户端模块，使用DID进行身份验证并获取访问令牌
- `did_auth_client.py`: DID认证客户端类，提供结构化的DID认证和令牌管理功能
- `jwt_config.py`: JWT配置模块，提供读取公钥和私钥的函数
- `test_token.py`: 测试脚本，用于测试完整的认证流程
- `private_key.pem` 和 `public_key.pem`: JWT签名使用的密钥对

## 安装与环境设置

本项目使用Poetry进行依赖管理和虚拟环境管理。

### 安装依赖

```bash
# 安装所有依赖
poetry install

# 激活虚拟环境
poetry shell
```

## 如何使用

### 启动服务器

在激活虚拟环境后，直接使用Python启动服务器：

```bash
# 进入examples_code目录
cd examples_code

# 直接使用Python启动服务器
python server.py
```

或者使用uvicorn启动：

```bash
# 使用uvicorn启动服务器
uvicorn examples_code.server:app --host 0.0.0.0 --port 8000 --reload
```

### 运行客户端

在激活虚拟环境后，直接使用Python启动客户端：

```bash
# 进入examples_code目录
cd examples_code

# 直接使用Python启动客户端
python client.py
```

或者使用模块方式运行：

```bash
# 使用Python模块方式运行客户端
python -m examples_code.client
```

## 客户端流程

`client.py` 使用 `DIDAuthClient` 类实现了以下流程：

1. **创建DID认证客户端**：
   - 使用DID文档路径和私钥路径初始化DIDAuthClient
   - DIDAuthClient负责加载DID文档和私钥，并管理认证头和令牌

2. **生成认证头和发送请求**：
   - 使用DIDAuthClient获取认证头（DID认证头或Bearer令牌）
   - 向服务器发送带有认证头的请求
   - 服务器验证认证头并生成JWT令牌
   - 服务器在响应头中返回JWT令牌

3. **管理令牌**：
   - DIDAuthClient从响应头中提取JWT令牌并存储
   - 后续请求自动使用存储的令牌
   - 如果令牌无效，DIDAuthClient会自动清除令牌并使用DID认证头重试

## DIDAuthClient类

`did_auth_client.py` 提供了 `DIDAuthClient` 类，它具有以下功能：

1. **认证头管理**：
   - 生成DID认证头
   - 存储和管理JWT令牌
   - 根据需要自动选择使用DID认证头或JWT令牌

2. **多域名支持**：
   - 为不同域名分别存储认证头和令牌
   - 根据请求URL自动选择正确的认证头

3. **令牌生命周期管理**：
   - 从响应头中提取和更新令牌
   - 清除单个域名的令牌或所有令牌

## 相关文件说明

### JWT密钥对

- `private_key.pem`: JWT签名使用的私钥，位于examples_code目录下
- `public_key.pem`: JWT验证使用的公钥，位于examples_code目录下

这对密钥用于服务器生成JWT令牌和验证JWT令牌。

### DID文档和私钥

示例使用了位于项目根目录下`use_did_test_public`文件夹中的DID文档和私钥：

- `use_did_test_public/did.json`: DID文档，已经注册到DID系统中
- `use_did_test_public/key-1_private.pem`: 与DID文档中公钥对应的私钥

这个DID文档已经注册，可以直接用于测试。DID文档中包含了公钥信息，私钥用于生成签名。

## 认证流程

1. 客户端使用DID文档和私钥生成认证头
2. 客户端发送带有认证头的请求到服务器
3. 服务器验证认证头，并生成JWT令牌
4. 服务器在响应头中返回JWT令牌
5. 客户端提取JWT令牌，并在后续请求中使用它
6. 服务器验证JWT令牌，并处理请求

## 配置说明

### 服务器配置

- `EXEMPT_PATHS`: 在`did_auth_middleware.py`中定义，这些路径不需要认证
- `WBA_SERVER_DOMAINS`: 在`did_auth_middleware.py`中定义，允许的服务器域名列表

### 客户端配置

- `SERVER_URL`: 在`client.py`中定义，服务器URL
- `TEST_ENDPOINT`: 在`client.py`中定义，测试端点
- `DID_DOCUMENT_PATH`: 在`client.py`中定义，DID文档路径
- `PRIVATE_KEY_PATH`: 在`client.py`中定义，私钥路径

## 调试提示

如果遇到问题，可以尝试以下方法：

1. 检查日志输出，了解认证流程中的问题
2. 确保`/test`路径不在`EXEMPT_PATHS`中，以便测试完整的认证流程
3. 检查CORS配置，确保`Authorization`头被正确暴露
4. 使用`test_token.py`脚本进行详细的调试

## 依赖项

- FastAPI: Web框架
- PyJWT: JWT处理
- cryptography: 密码学操作
- aiohttp: 异步HTTP客户端
- agent-connect: DID认证库 