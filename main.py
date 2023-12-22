from sqlalchemy import create_engine, URL, select, Table, MetaData, Column, Integer, String, UniqueConstraint,ForeignKey,DateTime,Float
from fastapi import FastAPI, Response, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Union
from sqlalchemy.orm import Session, declarative_base
from pydantic import BaseModel
from datetime import datetime
# from sqlalchemy.ext.declarative import declarative_base
# I like to launch directly and not use the standard FastAPI startup process.
# So, I include uvicorn
import uvicorn
from strawberry.fastapi import GraphQLRouter

sql_database_url = URL.create(
    drivername="mysql",
    username="admin",
    password="Stargod08122",
    host="database-4.caogqwqgw2no.us-east-1.rds.amazonaws.com",
    database="Tapioca4",
    port=3306
)

Base = declarative_base()
engine = create_engine(sql_database_url)
# Create tables
Base.metadata.create_all(bind=engine)
db = Session(engine)
def get_db():
    try:
        yield db
    finally:
        db.close()

class Customer(Base):
    __tablename__ = "Customer"
    CustomerID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String, nullable=False)
    Email = Column(String, unique=True, nullable=False)
    Phone = Column(String, unique=True, nullable=False)

class Order(Base):
    __tablename__ = "Order"
    OrderID = Column(Integer, primary_key=True, autoincrement=True)
    CustomerID = Column(Integer, ForeignKey('Customer.CustomerID'), nullable=False)
    StaffID = Column(Integer, ForeignKey('Staff.StaffID'), nullable=False)
    OrderTime = Column(DateTime, nullable=False)
    TotalPrice = Column(Float, nullable=False)
    Status = Column(String, nullable=False)

class Review(Base):
    __tablename__ = "Review"
    ReviewID = Column(Integer, primary_key=True, autoincrement=True)
    CustomerID = Column(Integer, ForeignKey('Customer.CustomerID'), nullable=False)
    OrderID = Column(Integer, ForeignKey('Order.OrderID'), nullable=False)
    Rating = Column(Float, nullable=False)
    Comment = Column(String, nullable=False)

class CustomerCreate(BaseModel):
    Name: str
    Email: str
    Phone: str

class CustomerResponse(BaseModel):
    CustomerID: int
    Name: str
    Email: str
    Phone: str

class OrderResponse(BaseModel):
    OrderID: int
    CustomerID: int
    StaffID: int
    OrderTime: datetime
    TotalPrice: float
    Status:str

class ReviewResponse(BaseModel):
    ReviewID: int
    CustomerID: int
    OrderID: int
    Rating: float
    Comment: str

app = FastAPI()

import strawberry
from typing import List

@strawberry.type
class graphCustomer:
    CustomerID: strawberry.ID
    Name: str
    Email: str
    Phone: str

@strawberry.type
class graphQuery:
    @strawberry.field
    def all_customers(self) -> List[graphCustomer]:
        # Replace with your logic to fetch customers from the database
        customers=db.query(Customer).all()
        return  [graphCustomer(CustomerID=c.CustomerID, Name=c.Name, Email=c.Email, Phone=c.Phone) for c in customers]

schema = strawberry.Schema(query=graphQuery)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/", response_model=List[CustomerResponse])
async def default(db: Session = Depends(get_db)):
    """
    Return all customers
    """
    customers = db.query(Customer).all()
    return customers
    
@app.get("/api/customers/", response_model=List[CustomerResponse])
async def get_all_customers(
    skip: int = Query(0, description="Skip the first N items", ge=0),
    limit: int = Query(5, description="Limit the number of items to retrieve", le=100),
    db: Session = Depends(get_db)
):
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers

@app.get("/api/customer/{customer_id}", response_model=CustomerResponse)
async def read_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Retrieve customer by ID.

    :param customer_id: Customer ID.
    :param db: Database session.
    :return: Customer data.
    """
    print("this customer id", customer_id)
    customer = db.query(Customer).filter_by(CustomerID=customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.post("/api/customer/", response_model=CustomerResponse)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """
    Create a new customer.

    :param customer: Customer data.
    :param db: Database session.
    :return: Created customer data.
    """
    customer = Customer(**customer.dict())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@app.put("/api/customer/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: int, customer: CustomerCreate, db: Session = Depends(get_db)):
    """
    Update the customer

    :param customer_id: Customer ID.
    :param customer: Customer data.
    :param db: Database session.
    :return: Updated customer data.
    """
    db_customer = db.query(Customer).filter_by(CustomerID=customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    for field, value in customer.dict().items():
        setattr(db_customer, field, value)

    db.commit()
    db.refresh(db_customer)
    return CustomerResponse(**db_customer.__dict__)

@app.delete("/api/customer/{customer_id}", response_model=CustomerResponse)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Delete the customer

    :param customer_id: Customer ID.
    :param db: Database session.
    :return: Deleted customer data.
    """
    db_customer = db.query(Customer).filter_by(CustomerID=customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(db_customer)
    db.commit()
    return CustomerResponse(**db_customer.__dict__)

@app.get("/api/customer/{customer_id}/order", response_model=List[OrderResponse])
def get_order(customer_id: int, db: Session = Depends(get_db)):
    """
    Get the orders of one customer

    :param customer_id: Customer ID.
    :param customer: Customer data.
    :param db: Database session.
    :return: Orders data of one customer.
    """
    order = db.query(Order).filter_by(CustomerID=customer_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    return order

@app.get("/api/customer/{customer_id}/review", response_model=List[ReviewResponse])
def get_review(customer_id: int, db: Session = Depends(get_db)):
    """
    Get the Reviews of one customer

    :param customer_id: Customer ID.
    :param customer: Customer data.
    :param db: Database session.
    :return: Reviews data of one customer.
    """
    review = db.query(Review).filter_by(CustomerID=customer_id)
    if review is None:
        raise HTTPException(status_code=404, detail="review not found")
    return review

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011)
