import AWS from 'aws-sdk'
import chai, { expect } from 'chai'
import dotenv from 'dotenv'
import { promises as fs } from 'fs'
import path from 'path'
import tmp, { DirectoryResult } from 'tmp-promise'

import { TempFileOnS3, tempFileOnS3, tempFileOnS3FromString } from './s3'
import { uuidHex } from './uuid-hex'

chai.use(require('chai-as-promised'))
chai.use(require('chai-string'))

dotenv.config({ path: path.join(__dirname, '..', '..', '.env') })

const EXAMPLE_FILENAME = 'example.txt'
const EXAMPLE_CONTENTS = `
foo
bar
baz
example
`

describe('S3 test helpers', () => {
  let integrationTestBucket: string
  before(() => {
    if (process.env.INTEGRATION_TEST_BUCKET === undefined) {
      throw Error('Expected INTEGRATION_TEST_BUCKET to be set')
    }
    integrationTestBucket = process.env.INTEGRATION_TEST_BUCKET
  })

  let s3: AWS.S3
  before(() => {
    s3 = new AWS.S3()
  })

  let sourceDir: DirectoryResult | undefined
  let sourcePath: string | undefined
  before(async () => {
    sourceDir = await tmp.dir()
    sourcePath = path.join(sourceDir.path, EXAMPLE_FILENAME)
    await fs.writeFile(sourcePath, EXAMPLE_CONTENTS, {
      encoding: 'utf-8',
    })
  })
  after(async () => {
    if (sourcePath) {
      await fs.unlink(sourcePath)
    }
    await sourceDir?.cleanup()
    sourceDir = undefined
  })

  describe('tempFileOnS3()', () => {
    context('given an explicit key', () => {
      const targetKey = `test_${uuidHex()}.txt`

      let result: TempFileOnS3 | undefined
      before(async () => {
        if (!sourcePath) {
          throw Error('sourcePath should be set')
        }

        result = await tempFileOnS3({
          localPath: sourcePath,
          bucket: integrationTestBucket,
          key: targetKey,
        })
      })

      it('returns the expected key', () => {
        expect(result).to.include({ key: targetKey })
      })

      it('creates the temporary file', async () => {
        if (!result) {
          throw Error('result should be set')
        }

        const fetched = await s3
          .getObject({ Bucket: integrationTestBucket, Key: targetKey })
          .promise()
        expect(fetched.Body?.toString()).to.equal(EXAMPLE_CONTENTS)
        expect(fetched.ETag).to.equal(result.eTag)
      })

      describe('on cleanup', () => {
        before(async () => {
          if (!result) {
            throw Error('result should be set')
          }

          await result.cleanup()
          result = undefined
        })

        it('removes the temporary file', async () => {
          await expect(
            s3
              .headObject({ Bucket: integrationTestBucket, Key: targetKey })
              .promise()
          )
            .to.eventually.be.rejectedWith(Error)
            .and.have.property('code', 'NotFound')
        })
      })
    })

    context('with an implicit key', () => {
      let result: TempFileOnS3 | undefined
      before(async () => {
        if (!sourcePath) {
          throw Error('sourcePath should be set')
        }

        result = await tempFileOnS3({
          localPath: sourcePath,
          bucket: integrationTestBucket,
        })
      })

      it('uses the expected key', () => {
        if (!result) {
          throw Error('result should be set')
        }
        expect(result.key).to.startWith('example_').and.endWith('.txt')
      })

      after(async () => {
        await result?.cleanup()
        result = undefined
      })
    })
  })

  describe('tempFileOnS3FromString()', () => {
    context('given an explicit key', () => {
      const targetKey = `test_${uuidHex()}.txt`

      let result: TempFileOnS3 | undefined
      before(async () => {
        if (!sourcePath) {
          throw Error('sourcePath should be set')
        }

        result = await tempFileOnS3FromString({
          contents: EXAMPLE_CONTENTS,
          bucket: integrationTestBucket,
          key: targetKey,
        })
      })

      it('returns the expected key', () => {
        expect(result).to.include({ key: targetKey })
      })

      it('creates the temporary file', async () => {
        if (!result) {
          throw Error('result should be set')
        }

        const fetched = await s3
          .getObject({ Bucket: integrationTestBucket, Key: targetKey })
          .promise()
        expect(fetched.Body?.toString()).to.equal(EXAMPLE_CONTENTS)
        expect(fetched.ETag).to.equal(result.eTag)
      })

      describe('on cleanup', () => {
        before(async () => {
          if (!result) {
            throw Error('result should be set')
          }

          await result.cleanup()
          result = undefined
        })

        it('removes the temporary file', async () => {
          await expect(
            s3
              .headObject({ Bucket: integrationTestBucket, Key: targetKey })
              .promise()
          )
            .to.eventually.be.rejectedWith(Error)
            .and.have.property('code', 'NotFound')
        })
      })
    })

    context('with an implicit key', () => {
      let result: TempFileOnS3 | undefined
      before(async () => {
        if (!sourcePath) {
          throw Error('sourcePath should be set')
        }

        result = await tempFileOnS3FromString({
          contents: EXAMPLE_CONTENTS,
          extension: '.txt',
          bucket: integrationTestBucket,
        })
      })

      it('uses the expected key', () => {
        if (!result) {
          throw Error('result should be set')
        }
        expect(result.key).to.endWith('.txt')
      })

      after(async () => {
        await result?.cleanup()
        result = undefined
      })
    })
  })
})
