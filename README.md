Software deployment is a critical phase in the software development lifecycle, where software is made available for users and systems to utilize. Ensuring that the deployed software functions as intended is an essential aspect of this process, known as deployment validation.

Deployment validation involves two key stages: pre-deployment and post-deployment. Before deployment, validation ensures the system is ready and in the appropriate state to receive updates or patches. After deployment, it confirms that the new updates do not disrupt existing functionality or performance, maintaining system stability and reliability.

This project focuses on automating the deployment validation process, both pre and post-deployment. It streamlines the validation procedures and provides a user-friendly interface to facilitate the validation process, ensuring that deployments are seamless, efficient, and error-free. Additionally, the automation reduces manual effort, minimizes the risk of human error, and accelerates the overall deployment cycle, contributing to a more robust and reliable software delivery process.

The project is developed using the Django framework, with each functional component organized into separate apps based on their specific roles: Home, PreDeployment, PostDeployment, Maintenance, and Backup. The Home app serves as the central hub, gathering relevant data from the user and directing the workflow to the appropriate apps according to user input. These apps then execute the designated tasks and return the results to the user.

Automation within the project is achieved through Bash scripting, while Python Selenium is utilized for web scraping tasks. The data collected through these automation processes is rendered to the frontend using Django. On the frontend, HTML, CSS, and JavaScript are employed to enhance the user experience, ensuring a smooth and intuitive interaction with the application.

To try the web app -
- Clone the project and install the requirements.txt.
- Go to path where manage.py exists. (deployment_checks/Deployment/manage.py)
- Execute the command "python manage.py runserver"

Here are some videos and snippets from the web app -

- Pre-deployment backup process

https://github.com/user-attachments/assets/ebd221cc-5310-461a-814d-f2767eddbe2d

- Post-deployment validation results

<img width="1437" alt="Screenshot 2024-08-25 at 11 12 01" src="https://github.com/user-attachments/assets/b1ba5c65-427d-4ce9-b59e-bcb211433718">

