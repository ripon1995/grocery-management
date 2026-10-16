# Grocery error messages
GROCERY_NOT_FOUND = 'Grocery with {grocery_id} not found'

# Market explore jobs (RabbitMQ queue + Redis job state), shared by the API and the worker
EXPLORE_JOBS_QUEUE = 'explore.jobs'
EXPLORE_JOB_KEY_PREFIX = 'market:explore:job'
