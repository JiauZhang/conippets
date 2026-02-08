from conippets.logger import FileLogger, getLogger

logger = FileLogger('file.log', 'file')
logger.debug('debug')
logger.critical('critical')
logger.error('error')
try:
    raise RuntimeError('runtime error.')
except:
    logger.exception('exception')

logger = getLogger('file')
logger.debug('getLogger')
logger.error('done')