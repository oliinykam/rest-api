from flask_restful import Resource
from flask import request, jsonify
from app.services.services import BookService
from app.database import get_db
from app.schemas.schemas import BookRequest, BookStatus, SortOrder
from pydantic import ValidationError
from pydantic_mongo import PydanticObjectId

def _book_to_dict(book) -> dict:
    return {
        "id": str(book.id),
        "title": book.title,
        "author": book.author,
        "release_year": book.release_year,
        "status": book.status,
        "description": book.description
    }

class HealthResource(Resource):
    def get(self):
        """
        Check API health.
        ---
        responses:
          200:
            description: Service is running
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: ok
        """
        return {"status": "ok"}, 200

class BookListResource(Resource):
    def get(self):
        """
        Get all books.
        ---
        parameters:
          - in: query
            name: sort_by
            type: string
            description: Field to sort by (e.g. title, author, release_year)
          - in: query
            name: order
            type: string
            enum: [asc, desc]
            default: asc
            description: Sort direction
          - in: query
            name: author
            type: string
            description: Filter by author name (case-insensitive partial match)
          - in: query
            name: status
            type: string
            enum: [available, issued]
            description: Filter by book status
          - in: query
            name: limit
            type: integer
            default: 10
            description: Maximum number of books to return
          - in: query
            name: offset
            type: integer
            default: 0
            description: Number of books to skip
        responses:
          200:
            description: Paginated list of books
            schema:
              $ref: '#/definitions/PaginatedBooksResponse'
          400:
            description: Invalid query parameters
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        sort_by = request.args.get("sort_by")
        order_str = request.args.get("order", "asc")
        author = request.args.get("author")
        status_str = request.args.get("status")
        
        try:
            limit = int(request.args.get("limit", 10))
            offset = int(request.args.get("offset", 0))
        except ValueError:
            return {"detail": "limit and offset must be integers"}, 400

        if limit < 1 or offset < 0:
            return {"detail": "Invalid limit or offset"}, 400

        status = None
        if status_str:
            try:
                status = BookStatus(status_str)
            except ValueError:
                return {"detail": "Invalid status"}, 400

        order = None
        if order_str:
            try:
                order = SortOrder(order_str)
            except ValueError:
                return {"detail": "Invalid order"}, 400

        service = BookService(get_db())
        items, total = service.get_books(
            sort_by=sort_by,
            order=order,
            author=author,
            status=status,
            limit=limit,
            offset=offset
        )

        def build_url(new_offset: int) -> str:
            params = dict(request.args)
            params["offset"] = str(new_offset)
            params["limit"] = str(limit)
            query_string = "&".join(f"{k}={v}" for k, v in params.items())
            base = request.base_url
            return f"{base}?{query_string}"

        next_page = build_url(offset + limit) if offset + limit < total else None
        prev_page = build_url(offset - limit) if offset > 0 else None

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "next_page": next_page,
            "prev_page": prev_page,
            "items": [_book_to_dict(b) for b in items]
        }, 200

    def post(self):
        """
        Create a new book.
        ---
        parameters:
          - in: body
            name: body
            schema:
              $ref: '#/definitions/BookRequest'
            required: true
            description: Book data to create
        responses:
          201:
            description: Book created successfully
            schema:
              $ref: '#/definitions/BookResponse'
          422:
            description: Validation error — invalid or missing fields
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        data = request.get_json(force=True)
        try:
            book_in = BookRequest(**data)
        except ValidationError as e:
            errors = e.errors()
            for err in errors:
                for k, v in err.items():
                    if not isinstance(v, (str, int, float, bool, list, dict, type(None))):
                        err[k] = str(v)
            return {"detail": errors}, 422

        service = BookService(get_db())
        result = service.create_book(book_in)
        return _book_to_dict(result), 201


class BookResource(Resource):
    def get(self, book_id: str):
        """
        Get a book by ID.
        ---
        parameters:
          - in: path
            name: book_id
            type: string
            required: true
            description: MongoDB ObjectId of the book
        responses:
          200:
            description: Book details
            schema:
              $ref: '#/definitions/BookResponse'
          400:
            description: Invalid ID format
            schema:
              $ref: '#/definitions/ErrorResponse'
          404:
            description: Book not found
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        try:
            pid = PydanticObjectId(book_id)
        except Exception:
            return {"detail": "Invalid ID format"}, 400

        service = BookService(get_db())
        book = service.get_book(pid)
        if not book:
            return {"detail": "Book not found"}, 404

        return _book_to_dict(book), 200

    def delete(self, book_id: str):
        """
        Delete a book.
        ---
        parameters:
          - in: path
            name: book_id
            type: string
            required: true
            description: MongoDB ObjectId of the book to delete
        responses:
          204:
            description: Book deleted successfully
          400:
            description: Invalid ID format
            schema:
              $ref: '#/definitions/ErrorResponse'
          404:
            description: Book not found
            schema:
              $ref: '#/definitions/ErrorResponse'
        """
        try:
            pid = PydanticObjectId(book_id)
        except Exception:
            return {"detail": "Invalid ID format"}, 400

        service = BookService(get_db())
        success = service.delete_book(pid)
        if not success:
            return {"detail": "Book not found"}, 404

        return "", 204