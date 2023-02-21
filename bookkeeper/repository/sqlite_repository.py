 from inspect import get_annotations
 import sqlite3
class SQLiteRepository(AbstractRepository[T]):
    """
    Репозиторий для хранения в sqlite.
    """
    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')

    def add(self, obj: T) -> int:
        names = ', '.join(self.fields.keys())
        p = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(
            f'INSERT INTO {self.table_name} ({names}) VALUES ({p})',
            values
            )
            obj.pk = cur.lastrowid
        con.close()
        return obj.pk

    def get(self, pk: int) -> T | None:
        # return self._container.get(pk)
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            sql_cmd = f"SELECT * FROM {self.table_name} WHERE " + self.get_primary_key(table=self.table_name,
                                                                                  database=self.db_file) + "=?;"
            fetch = cursor.execute(sql_cmd, (pk,))


    def delete(self, pk: int) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f"DELETE FROM {self.table_name} WHERE id=?",(pk,))
        con.commit()
        con.close()

    def update(self, obj: T) -> None:
        if obj.pk == 0:
            raise ValueError('attempt to update object with unknown primary key')
        # self._container[obj.pk] = obj
        names = ', '.join(self.fields.keys())
        p = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f"UPDATE {self.table_name} SET ({names}) VALUES ({p})",
            values
            )
        con.commit()
        con.close()

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        if where is None:
            return list(self._container.values())
        return [obj for obj in self._container.values()
                if all(getattr(obj, attr) == value for attr, value in where.items())]
