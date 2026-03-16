import AWS from 'aws-sdk'
import { promises as fs } from 'fs'
import path from 'path'

import { uuidHex } from './uuid-hex'

// Inline equivalent of Node's `BufferEncoding` type, defined here to avoid
// making `@types/node` a transitive dependency. To keep this up to date, refer
// to `BufferEncoding` in types/node/buffer.d.ts in DefinitelyTyped:
// https://github.com/DefinitelyTyped/DefinitelyTyped/blob/master/types/node/buffer.d.ts
type BufferEncoding =
  | 'ascii'
  | 'utf8'
  | 'utf-8'
  | 'utf16le'
  | 'utf-16le'
  | 'ucs2'
  | 'ucs-2'
  | 'base64'
  | 'base64url'
  | 'latin1'
  | 'binary'
  | 'hex'

async function writeTempFile({
  key,
  bucket,
  contents,
}: {
  key: string
  bucket: string
  contents: Buffer | string
}): Promise<{ eTag: string; cleanup: () => Promise<void> }> {
  const s3 = new AWS.S3()

  const { ETag: eTag } = await s3
    .upload({ Bucket: bucket, Key: key, Body: contents })
    .promise()

  return {
    eTag,
    async cleanup(): Promise<void> {
      await s3.deleteObject({ Bucket: bucket, Key: key as string }).promise()
    },
  }
}

export interface TempFileOnS3 {
  key: string
  eTag: string
  cleanup(): Promise<void>
}

/*
 * Copy the given path to S3. Provide a cleanup function which deletes the
 * object.
 */
export async function tempFileOnS3({
  localPath,
  bucket,
  key,
  encoding,
  verbose = false,
}: {
  localPath: string
  bucket: string
  key?: string
  encoding?: BufferEncoding
  verbose?: boolean
}): Promise<TempFileOnS3> {
  if (!key) {
    const { name, ext } = path.parse(localPath)
    key = `${name}_${uuidHex()}${ext}`
  }

  const s3Url = `s3://${bucket}/${key}`
  if (verbose) {
    console.error(`Uploading ${localPath} to ${s3Url}`)
  }

  const contents = await fs.readFile(localPath, encoding)

  const { eTag, cleanup } = await writeTempFile({
    bucket,
    key,
    contents,
  })

  return {
    key,
    eTag,
    async cleanup(): Promise<void> {
      if (verbose) {
        console.error(`Removing ${s3Url}`)
      }
      await cleanup()
    },
  }
}

/*
 * Write the given contents to S3. Provide a cleanup function which deletes the
 * object.
 */
export async function tempFileOnS3FromString({
  contents,
  bucket,
  key,
  extension = '',
  verbose = false,
}: {
  contents: string
  bucket: string
  key?: string
  extension?: string
  verbose?: boolean
}): Promise<TempFileOnS3> {
  if (!key) {
    key = `${uuidHex()}${extension}`
  }

  const s3Url = `s3://${bucket}/${key}`
  if (verbose) {
    console.error(`Writing to ${s3Url}`)
  }

  const { eTag, cleanup } = await writeTempFile({
    bucket,
    key,
    contents,
  })

  return {
    key,
    eTag,
    async cleanup(): Promise<void> {
      if (verbose) {
        console.error(`Removing ${s3Url}`)
      }
      await cleanup()
    },
  }
}
