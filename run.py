from app.users import crt_db
from app import get_app

if __name__ == "__main__":
    crt_db()

    app = get_app()
    app.run(debug=True, host='0.0.0.0')




# import datetime

# td = datetime.datetime.now()
# formatted_time = td.strftime("%Y-%m-%d %H:%M:%S")
# print(formatted_time)
# print(td.timestamp())