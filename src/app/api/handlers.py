import json

from tornado.web import RequestHandler

from app.db.storage import ScheduleQuery


class ScheduleQueryHandler(RequestHandler):
    SUPPORTED_METHODS = ["GET", "PUT"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.schedule_query = ScheduleQuery(self.db)

    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

    async def get(self, user_id):
        schedule_query = await self.schedule_query.find(user_id=user_id)
        if schedule_query:
            self.set_status(200)
            self.write(self.serialize(
                schedule_query['user_id'],
                schedule_query['query'],
                schedule_query['query_type'],
            ))
        else:
            self.set_status(404)

    async def put(self, user_id):
        body = self.request.body

        if not body:
            self.set_status(400)
            self.write(self.serialize_error_detail("Body can't be empty"))
            return

        body_json = json.loads(body)
        user_id, query, query_type = (int(user_id),
                                      body_json['query'],
                                      body_json['query_type'])

        if query and query_type:
            await self.schedule_query.save(user_id, query, query_type)
            self.set_status(200)
            self.write(self.serialize(user_id, query, query_type))
        else:
            self.set_status(400)
            self.write(self.serialize_error_detail("Query can't be empty"))

    @staticmethod
    def serialize(user_id, query, query_type):
        return json.dumps({
            'user_id': user_id,
            'query': query,
            'query_type': query_type
        }, ensure_ascii=False)

    @staticmethod
    def serialize_error_detail(detail):
        return json.dumps({
            'detail': detail,
        })

    @property
    def db(self):
        return self.application.settings['db']
