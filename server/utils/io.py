import io
import aiofiles

##############################################################################################################################

# 定义写入大小
CHUNK_SIZE = 1024 * 1024


async def write_file(filePath, source: io.BytesIO):
    async with aiofiles.open(filePath, 'wb') as out_file:
        while content := await source.read(CHUNK_SIZE):
            await out_file.write(content)


async def read_file(filePath):
    async with aiofiles.open(filePath, 'rb') as file:
        while content := await file.read(CHUNK_SIZE):
            yield content

##############################################################################################################################