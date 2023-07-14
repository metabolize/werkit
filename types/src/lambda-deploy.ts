import AWS from 'aws-sdk'

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
    const lambdaClient = new AWS.Lambda({ region })
    await lambdaClient
      .createFunction({
        FunctionName: functionName,
        Runtime: runtime,
        Role: role,
        Handler: handler,
        Environment: { Variables: envVars },
        Code: { S3Bucket: s3CodeBucket, S3Key: key },
        ...(timeoutSeconds ? { Timeout: timeoutSeconds } : undefined),
        ...(memorySizeMb ? { MemorySize: memorySizeMb } : undefined),
      })
      .promise()

    await lambdaClient
      .waitFor('functionUpdated', {
        FunctionName: functionName,
        $waiter: { delay: 1, maxAttempts: 60 },
      })
      .promise()
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
  await new AWS.Lambda({ region })
    .deleteFunction({ FunctionName: functionName })
    .promise()
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
    const lambdaClient = new AWS.Lambda({ region })
    await lambdaClient
      .updateFunctionCode({
        S3Bucket: s3CodeBucket,
        S3Key: key,
        FunctionName: functionName,
      })
      .promise()
    await lambdaClient
      .waitFor('functionUpdated', {
        FunctionName: functionName,
        $waiter: { delay: 1, maxAttempts: 60 },
      })
      .promise()
    if (verbose) {
      console.error(`Lambda function ${functionName} updated`)
    }
  } finally {
    await cleanup()
  }
}
