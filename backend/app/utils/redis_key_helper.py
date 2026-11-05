from enum import Enum


class RedisKeyHelper(str, Enum):
    # static keys
    GROCERIES = "groceries"

    # dynamic keys
    GROCERY_DETAIL = 'grocery:{grocery_id}:detail'

    # Market explore jobs
    EXPLORE_JOB_KEY_PREFIX = 'market:explore:job'

    # Email jobs
    EMAIL_JOB_KEY_PREFIX = 'email:job'

    def build_key(self, **kwargs) -> str:
        """Helper method to easily inject dynamic variables into the key template."""
        return self.value.format(**kwargs)
