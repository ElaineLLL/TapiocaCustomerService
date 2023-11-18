#
# FastAPI is a framework and library for implementing REST web services in Python.
# https://fastapi.tiangolo.com/
#
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Union

# I like to launch directly and not use the standard FastAPI startup process.
# So, I include uvicorn
import uvicorn
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Query, Response, status
from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the Customer model
Base = declarative_base()
class Customer(Base):
    __tablename__ = "customers"
    CustomerID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String, nullable=False)
    Email = Column(String, unique=True, nullable=False)
    Phone = Column(String, unique=True, nullable=False)

# connect to the RDS database
engine = create_engine("your_database_connection_string")
Base.metadata.create_all(bind=engine)
# create a Sessionlocal class for deoendency injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Set up Fastapi application
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
# ******************************
#
# DFF TODO Show the class how to do this with a service factory instead of hard code.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#
# END TODO
# **************************************
#create a customer
@app.post("/api/customer", response_model=Customer)
def create_customer(customer: Customer, db: Session = Depends(get_db)):
    """
    Create a new customer.

    :param customer: Customer data to be created.
    :param db: Database session.
    :return: Created customer data.
    """
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

def read_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Retrieve customer by ID.

    :param customer_id: Customer ID.
    :param db: Database session.
    :return: Customer data.
    """
    customer = db.query(Customer).filter(Customer.CustomerID == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
    
@app.put("/api/customer/{customer_id}", response_model=Customer)
def update_customer(customer_id: int, updated_customer: Customer, db: Session = Depends(get_db)):
    """
    Update customer by ID.

    :param customer_id: Customer ID.
    :param updated_customer: Updated customer data.
    :param db: Database session.
    :return: Updated customer data.
    """
    existing_customer = db.query(Customer).filter(Customer.CustomerID == customer_id).first()
    if existing_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Update fields
    existing_customer.Name = updated_customer.Name
    existing_customer.Email = updated_customer.Email
    existing_customer.Phone = updated_customer.Phone

    db.commit()
    db.refresh(existing_customer)
    return existing_customer

@app.delete("/api/customer/{customer_id}", response_model=Customer)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Delete customer by ID.

    :param customer_id: Customer ID.
    :param db: Database session.
    :return: Deleted customer data.
    """
    customer = db.query(Customer).filter(Customer.CustomerID == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()
    return customer

@app.get("/api/customer/", response_model=list[Customer])
def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: str = None,
    email: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Customer)

    if name:
        query = query.filter(Customer.Name == name)
    if email:
        query = query.filter(Customer.Email == email)

    customers = query.offset(skip).limit(limit).all()
    return customers
# @app.post("/api/customers/", response_model=Customer)
# def create_customer(customer: Customer):
#     customers.append(customer)
#     return customer

# @app.get("/api/customers/{customer_id}", response_model=Customer)
# def read_customer(customer_id: int):
#     """
#     Return a customer based on customer_id.
#     - **customer_id**: customer's id
#     """
#     for customer in customers:
#         if customer.CustomerID == customer_id:
#             return customer
#     return None

# @app.put("/api/customers/{customer_id}", response_model=Customer)
# def update_customer(customer_id: int, customer: Customer):
#     for i, existing_customer in enumerate(customers):
#         if existing_customer.CustomerID == customer_id:
#             customers[i] = customer
#             return customer
#     return None

# @app.delete("/api/customers/{customer_id}", response_model=Customer)
# def delete_customer(customer_id: int):
#     for i, customer in enumerate(customers):
#         if customer.CustomerID == customer_id:
#             return customers.pop(i)
#     return None


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011)