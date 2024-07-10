from database import Databases


class CRUD(Databases):
    def insertDB(self, table, columns, values):
        query = f"INSERT INTO {table} ({columns}) VALUES (%s, %s, %s)"
        self.cursor.execute(query, values)
        self.commit()

    def readDB(self, table, column):
        sql = " SELECT {column} from {table}".format(column=column, table=table)
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except Exception as e:
            result = (" read DB err", e)

        return result

    def updateDB(self, table, column, value, condition):
        sql = " UPDATE {table} SET {column}='{value}' WHERE {column}='{condition}' ".format(table=table,
                                                                                            column=column,
                                                                                            value=value,
                                                                                            condition=condition)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(" update DB err", e)

    def deleteDB(self, table, condition):
        sql = " delete from {table} where {condition} ; ".format(table=table,
                                                                 condition=condition)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print("delete DB err", e)

    def insertPressDB(self, title, content, original_url, published_at, image_url, total_content_line, authors,
                      language, publisher, access_level, category):
        sql = ("INSERT INTO press(title, content, original_url, published_at, image_url, total_content_line, author,"
               " language, publisher, access_level, category) VALUES "
               "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;")

        try:
            self.cursor.execute(sql, (
                title, content, original_url, published_at, image_url, total_content_line, authors, language, publisher,
                 access_level, category))
            self.db.commit()
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(" insert DB err: ", e)

    def insertPressDB(self, title, content, original_url, published_at, image_url, total_content_line, authors,
                      language, publisher, access_level, category):
        sql = ("INSERT INTO press(title, content, original_url, published_at, image_url, total_content_line, author,"
               " language, publisher, access_level, category) VALUES "
               "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;")

        try:
            self.cursor.execute(sql, (
                title, content, original_url, published_at, image_url, total_content_line, authors, language, publisher,
                 access_level, category))
            self.db.commit()
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(" insert DB err: ", e)

    def check_exist_url(self, original_url):
        sql = "SELECT * from press where original_url = %s"
        try:
            self.cursor.execute(sql, (original_url,))
            result = self.cursor.fetchone()[0]
            print(result)
            return result
        except Exception as e:
            print(" read DB err: ", e)

    def insertPressContentDB(self, press_id, line_number, content):
        sql = "INSERT INTO press_content_line(press_id, line_number, line_text) VALUES (%s, %s, %s);"
        try:
            self.cursor.execute(sql, (press_id, line_number, content))
            self.db.commit()
        except Exception as e:
            print(" insert DB err: ", e)

    def insertPressYoutubeContentDB(self, press_id, line_number, content, start_sec, end_sec):
        sql = "INSERT INTO press_content_line(press_id, line_number, line_text, start_sec, end_sec) VALUES (%s, %s, %s, %s ,%s);"
        try:
            self.cursor.execute(sql, (press_id, line_number, content, start_sec, end_sec))
            self.db.commit()
        except Exception as e:
            print(" insert DB err: ", e)

    # 문장 끝에 특정 문자가 있는 데이터만 선택
    def selectPressContentLine(self):
        sql = "SELECT id, line_text, translated_line_text FROM press_content_line WHERE line_text LIKE '%!@!'"
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print("Read DB Error: ", e)

    def updatePressContentLine(self, line_id, line_text, translated_line_text):
        sql = "UPDATE press_content_line SET line_text = %s, translated_line_text = %s WHERE id = %s"
        try:
            self.cursor.execute(sql, (line_text, translated_line_text, line_id))
            self.db.commit()
        except Exception as e:
            print("Update DB Error: ", e)

    def update_press_content(self):
        # 모든 press 레코드 가져오기
        self.cursor.execute("SELECT id, content FROM press")
        press_records = self.cursor.fetchall()

        for record in press_records:
            press_id, content = record
            # 기존 content를 3줄로 자르기
            trimmed_content = trim_content_to_three_lines(content)

            # content 업데이트
            self.cursor.execute(
                "UPDATE press SET content = %s WHERE id = %s",
                (trimmed_content, press_id)
            )

        # 변경사항 커밋
        self.db.commit()
        print("Press content updated successfully")


def trim_content_to_three_lines(content):
    lines = content.split('\n')
    return '\n'.join(lines[:3])

