from abc import ABC, abstractmethod

class Task(ABC):
    @abstractmethod
    def execute(self):
        pass

class BackupTask(Task):
    def execute(self):
        print("Executing backup task: saving data.")

class EmailTask(Task):
    def execute(self):
        print("Sending an email notification.")


tasks = [BackupTask(), EmailTask()]
for t in tasks:
    t.execute()

