from sqlalchemy import create_engine, URL, select, Table, MetaData, Column, Integer, String, UniqueConstraint
from fastapi import FastAPI, Response, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Union
from sqlalchemy.orm import Session, declarative_base
from pydantic import BaseModel
# from sqlalchemy.ext.declarative import declarative_base
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
Base = declarative_base()

# engine = create_engine(sql_database_url)
# # Assuming you have a MetaData object that reflects your database
# metadata = MetaData()
# metadata.bind = engine
# metadata.reflect(engine)
# print("All tables:", metadata.tables.keys())
# customer_table = Table('Customer', metadata, autoload=True, autoload_with=engine)

engine = create_engine(sql_database_url)
# Create tables
Base.metadata.create_all(bind=engine)
def get_db():
    db = Session(engine)
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

@app.get("/")
async def default(db: Session = Depends(get_db)):
    """
    Return all customers
    """
    customers = db.query(Customer).all()
    return customers
    
@app.get("/api/customer/{customer_id}", response_model=None)
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

    # select_query = select(customer_table.c.Name, customer_table.c.Email, customer_table.c.Phone).where(customer_table.c.CustomerID == customer_id)
    # # Execute the query and fetch the result
    # with engine.connect() as connection:
    #     result = connection.execute(select_query)
    #     customer = result.fetchone()
    #     # rows = result.fetchall()
    #     print(customer)
    # if customer is None:
    #     raise HTTPException(status_code=404, detail="Customer not found")
    # return {"CustomerID": customer_id, "Name": customer[0], "Email": customer[1], "Phone": customer[2]}

class CustomerCreate(BaseModel):
    Name: str
    Email: str
    Phone: str
class CustomerResponse(BaseModel):
    CustomerID: int
    Name: str
    Email: str
    Phone: str
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

# Update customer by ID
@app.put("/api/customer/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, customer: CustomerCreate, db: Session = Depends(get_db)):
    db_customer = db.query(Customer).filter_by(CustomerID=customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    for field, value in customer.dict().items():
        setattr(db_customer, field, value)

    db.commit()
    db.refresh(db_customer)
    return CustomerResponse(**db_customer.__dict__)

# Delete customer by ID
@app.delete("/api/customer/{customer_id}", response_model=CustomerResponse)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = db.query(Customer).filter_by(CustomerID=customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(db_customer)
    db.commit()
    return CustomerResponse(**db_customer.__dict__)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011)
