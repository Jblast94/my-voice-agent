# Use a standard Python base image for simplicity
FROM python:3.10

WORKDIR /home/user/app

# Install app dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create a non-root user
RUN useradd -m -u 1000 user && chown -R user:user /home/user/app

# Switch to the non-root user
USER user

# Expose the port
EXPOSE 7860

# Command to run the app
CMD ["python", "app.py"]