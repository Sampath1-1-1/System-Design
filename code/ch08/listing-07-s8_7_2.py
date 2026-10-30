# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.7.2 (listing 7). Edit the manuscript, not this file.
import asyncio


class DataLoader:
    """Coalesce every load(key) issued in the same event-loop tick into one batch call."""

    def __init__(self, batch_fn):
        self.batch_fn = batch_fn          # async fn: list[key] -> list[value], same order
        self.cache = {}                   # key -> Future (per-request memoization)
        self.queue = []                   # keys waiting for the next dispatch

    def load(self, key):
        if key in self.cache:
            return self.cache[key]
        fut = asyncio.get_running_loop().create_future()
        self.cache[key] = fut
        self.queue.append(key)
        if len(self.queue) == 1:          # first key in this tick: schedule a dispatch
            asyncio.get_running_loop().call_soon(
                lambda: asyncio.ensure_future(self._dispatch()))
        return fut

    async def _dispatch(self):
        keys, self.queue = self.queue, []
        try:
            values = await self.batch_fn(keys)
            for k, v in zip(keys, values):
                self.cache[k].set_result(v)
        except Exception as exc:           # fail every waiter, not just one
            for k in keys:
                self.cache[k].set_exception(exc)


queries = []
AUTHORS = {1: "Ada", 2: "Linus", 3: "Grace"}


async def fetch_authors(ids):
    queries.append(f"SELECT id, name FROM authors WHERE id IN {tuple(ids)}")
    return [AUTHORS.get(i) for i in ids]


async def main():
    loader = DataLoader(fetch_authors)    # create one loader PER REQUEST
    posts = [{"id": 10, "author_id": 1}, {"id": 11, "author_id": 2},
             {"id": 12, "author_id": 1}, {"id": 13, "author_id": 3}]
    names = await asyncio.gather(*(loader.load(p["author_id"]) for p in posts))
    print(names)     # ['Ada', 'Linus', 'Ada', 'Grace']
    print(queries)   # ['SELECT id, name FROM authors WHERE id IN (1, 2, 3)']


asyncio.run(main())
