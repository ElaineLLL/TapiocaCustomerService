from sqlalchemy import create_engine, URL, select, Table, MetaData, Column, Integer, String, UniqueConstraint
from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Union

from sqlalchemy.orm import Session, declarative_base
# I like to launch directly and not use the standard FastAPI startup process.
# So, I include uvicorn
import uvicorn

app = FastAPI()

sql_database_url = URL.create(
    drivername="mysql",
    username="admin",
    password="Stargod08122",
    host="database-1.caogqwqgw2no.us-east-1.rds.amazonaws.com",
    database="Tapioca",
    port=3306
)

engine = create_engine(sql_database_url)
# Assuming you have a MetaData object that reflects your database
metadata = MetaData()
metadata.bind = engine
metadata.reflect(engine)
print("All tables:", metadata.tables.keys())

customer_table = Table('Customer', metadata, autoload=True, autoload_with=engine)

Base = declarative_base()
class Customer(Base):
    __tablename__ = "customers"
    CustomerID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String, nullable=False)
    Email = Column(String, unique=True, nullable=False)
    Phone = Column(String, unique=True, nullable=False)

@app.get("/")
async def default():
    """
    Return all customers
    """
    return {"CustomerID": 1, "Name": "John Doe", "Email": "john@example.com", "Phone": "123-456-7890"}
    
@app.get("/api/customer/{customer_id}", response_model=Customer)
def read_customer(customer_id: int):
    """
    Retrieve customer by ID.

    :param customer_id: Customer ID.
    :param db: Database session.
    :return: Customer data.
    """
    select_query = select(customer_table.c.Name, customer_table.c.Email, customer_table.c.Phone).where(customer_table.c.CustomerID == customer_id)
    # Execute the query and fetch the result
    with engine.connect() as connection:
        result = connection.execute(select_query)
        customer = result.fetchone()
        # rows = result.fetchall()
        print(customer)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

select_query=select(customer_table)
# Create a SELECT query for Name, Email, and Phone based on CustomerID
