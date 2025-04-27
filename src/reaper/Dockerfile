# Use the official Python runtime as a parent image
FROM python:3.9.18-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# ENV NGROK_AUTHTOKEN=2WlOppnSclFQbpFBerTP7k5k7Pp_6QPqLbDnzadavYb45vbE4
ENV NGROK_LISTENER_RUNNING=false
ENV RENDER_EXTERNAL_HOSTNAME=https://breatheeasyapp.onrender.com/
ENV DEBUG=False
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/staticfiles

RUN chmod -R 755 /app/staticfiles

RUN python manage.py collectstatic --no-input
# Make port 8000 available to the world outside this container
EXPOSE 8000

RUN python manage.py makemigrations

RUN python manage.py migrate
# Run app.py when the container launches
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
#["python", "manage.py", "runserver", "0.0.0.0:8000"]
