from app import app, start_subscriber_thread

start_subscriber_thread()

if __name__ == "__main__":
    app.run()
