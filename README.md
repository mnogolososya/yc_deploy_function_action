# 🚀 Deploy cloud function to Yandex.Cloud

Deploy new or update serverless function on Yandex.Cloud

## Example usage

```
uses: mnogolososya/yc_deploy_function_action@v1.4.0
with:
  yc_account_id: ${{ secrets.YC_LAMBDA_DEPLOY_ACCOUNT_ID }}
  yc_key_id: ${{ secrets.YC_LAMBDA_DEPLOY_KEY_ID }}
  yc_private_key: ${{ secrets.YC_LAMBDA_DEPLOY_PRIVATE_KEY }}
  function_name: 'my-glorious-function'
  function_description: 'hello there'
  runtime: 'python39-preview'
  version_description: 'what a version!'
  function_entrypoint: 'example.code_to_deploy.handler'
  memory: 256
  execution_timeout: 7
  source_dir: './example'
  folder_id: 'b1ghsls4prhgto9om121'
  foo: 'bar'
  debug: '1'
```

## Inputs configuration

| Key | Value | Required |
| ------------- | ------------- | ------------- |
| `yc_account_id` | YandexCloud account id | **Yes** |
| `yc_key_id` | YandexCloud trusted key id | **Yes** |
| `yc_private_key` | YandexCloud private key | **Yes** |
| `function_name` | Name of a function to deploy | **Yes** |
| `runtime` | Function runtime | **Yes** |
| `folder_id` | Function folder id | **Yes** |
| `function_entrypoint` | Entry point of function| No |
| `function_description` | Function description | No |
| `version_description` | New function version description | No |
| `source_dir` | Directory with function code to deploy. Default value is `.` (root directory of repository) | No |
| `memory` |  Memory limit in `megabytes` for function in Yandex Cloud Default value is `128` | No |
| `execution_timeout` | Execution timeout in seconds for function in Yandex Cloud. Default value is `15` | No |
