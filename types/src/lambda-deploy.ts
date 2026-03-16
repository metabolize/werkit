import {
  CreateFunctionCommand,
  DeleteFunctionCommand,
  LambdaClient,
  UpdateFunctionCodeCommand,
  waitUntilFunctionUpdated,
} from '@aws-sdk/client-lambda'

import { tempFileOnS3 } from './s3'

export const DEFAULT_RUNTIME = 'nodejs14.x'

export async function createFunction({
  region,
  functionName,
  handler,
  role,
  localPathToZipfile,
  s3CodeBucket,
  timeoutSeconds,
  memorySizeMb,
  runtime = DEFAULT_RUNTIME,
  envVars = {},
  verbose = false,
}: {
  region: string
  functionName: string
  handler: string
  role: string
  localPathToZipfile: string
  s3CodeBucket: string
  timeoutSeconds?: number
  memorySizeMb?: number
  runtime?: string
  envVars?: { [k: string]: string }
  verbose?: boolean
}): Promise<void> {
  const { cleanup, key } = await tempFileOnS3({
    localPath: localPathToZipfile,
    bucket: s3CodeBucket,
    verbose,
  })

  try {
    const lambdaClient = new LambdaClient({ region })
    await lambdaClient.send(
      new CreateFunctionCommand({
        FunctionName: functionName,
        Runtime: runtime,
        Role: role,
        Handler: handler,
        Environment: { Variables: envVars },
        Code: { S3Bucket: s3CodeBucket, S3Key: key },
        ...(timeoutSeconds ? { Timeout: timeoutSeconds } : undefined),
        ...(memorySizeMb ? { MemorySize: memorySizeMb } : undefined),
      }),
    )

    await waitUntilFunctionUpdated(
      { client: lambdaClient, maxWaitTime: 60 },
      { FunctionName: functionName },
    )
    if (verbose) {
      console.error(`Lambda function ${functionName} created`)
    }
  } finally {
    await cleanup()
  }
}

export async function deleteFunction({
  region,
  functionName,
}: {
  region: string
  functionName: string
}): Promise<void> {
  await new LambdaClient({ region }).send(
    new DeleteFunctionCommand({ FunctionName: functionName }),
  )
}

export async function updateFunctionCode({
  functionName,
  region,
  s3CodeBucket,
  localPathToZipfile,
  verbose,
}: {
  functionName: string
  region: string
  s3CodeBucket: string
  localPathToZipfile: string
  verbose?: boolean
}): Promise<void> {
  const { cleanup, key } = await tempFileOnS3({
    localPath: localPathToZipfile,
    bucket: s3CodeBucket,
    verbose,
  })

  try {
    const lambdaClient = new LambdaClient({ region })
    await lambdaClient.send(
      new UpdateFunctionCodeCommand({
        S3Bucket: s3CodeBucket,
        S3Key: key,
        FunctionName: functionName,
      }),
    )
    await waitUntilFunctionUpdated(
      { client: lambdaClient, maxWaitTime: 60 },
      { FunctionName: functionName },
    )
    if (verbose) {
      console.error(`Lambda function ${functionName} updated`)
    }
  } finally {
    await cleanup()
  }
}
