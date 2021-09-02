# YandexCloud serverless function deploy action

Deploy new serverless function version (including function creation if it does not exist).

## Inputs

## `yc_account_id`

YandexCloud account id **(Required)**

## `yc_key_id`

YandexCloud trusted key id **(Required)**

## `yc_private_key`

YandexCloud private key **(Required)**

## `function_name`

Function name **(Required)**

## `function_description`

Function description **(Required)**

## `runtime`

Runtime for function **(Required)**

## `version_description`

New function version description **(Required)**

## `function_entrypoint`

Entrypoint for function **(Required)**

## `memory`

Maximum allowed memory for function in MB

## `execution_timeout`

Maximum allowed time for function to execute in seconds

## `source_dir`

Path to directory with code to deploy **(Required)**

## `folder_id`

Function folder id **(Required)**

## Example usage

```
uses: mnogolososya/yc_deploy_function_action@v1.0
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