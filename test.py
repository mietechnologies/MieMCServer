from util import logger

logger.start('this is a test start')

for index in range(40):
    logger.log('this is a test [{}]'.format(index))