import uvicorn


def main():
    uvicorn.run("kanot.main:app", reload=True)

if __name__ == "__main__":
    main()
