import json
import os
from datetime import datetime


class Node:
    def __init__(self, node_id, node_type, label, actions=None, condition=None):
        self.node_id = node_id
        self.node_type = node_type
        self.label = label
        self.actions = actions or []
        self.condition = condition

    def process(self, context):
        """
        Process the node. Executes actions and evaluates conditions.
        """
        print(f"Processing Node: {self.label}")
        if self.actions:
            for action in self.actions:
                exec(action, {'context': context})
        if self.node_type == "condition_node" and self.condition:
            return eval(self.condition, {'context': context})
        return None


class AutomationEngine:
    def __init__(self, flowchart_data):
        self.nodes = {}
        self.rules = flowchart_data.get("rules", [])
        self._build_nodes(flowchart_data.get("nodes", {}))

    def _build_nodes(self, nodes_data):
        for node_id, node_data in nodes_data.items():
            node = Node(
                node_id=node_data["id"],
                node_type=node_data["type"],
                label=node_data["label"],
                actions=node_data.get("actions"),
                condition=node_data.get("condition"),
            )
            self.nodes[node_id] = node

    def find_next_node(self, current_node_id, condition_result):
        """
        Find the next node based on the current node and condition result.
        """
        for rule in self.rules:
            if rule["start"] == current_node_id:
                if rule["conditionResult"] == condition_result or rule["conditionResult"] is None:
                    return rule["end"]
        return None

    def run(self, context):
        """
        Execute the flowchart starting from a specific node.
        """
        current_node_id = 'BEGIN'
        while current_node_id:
            current_node = self.nodes[current_node_id]
            condition_result = current_node.process(context)
            if isinstance(condition_result, bool):
                condition_result = "true" if condition_result else "false"
            current_node_id = self.find_next_node(
                current_node_id, condition_result)


# Sample context for testing
class Context:
    def __init__(self, profile):
        self.profile = profile
        self.current_date = datetime.now().strftime("%m-%d")

    def load_profile_720_view(self):
        print(f"[ Loading profile 720 view: { self.profile['name'] } ] \n ")
        self.current_profile_index = 0  # Start with the first profile

    def is_birthday(self):
        # Extract the day and month from the profile's birthday
        profile_birthday = "-".join(self.profile['birthday'].split("-")[1:])  # Extract 'MM-dd'
        
        print(
            f"Checking if current date ({self.current_date}) equals birthday ({profile_birthday}) for {self.profile['name']}"
        )
        
        return profile_birthday == self.current_date

    # TODO add more condition_node

    def send_email(self, template_id):
        if self.profile is None:
            print("No profile to send email.")
            return
        print(
            f"\n [Sending email to {self.profile['name']} with template ID: {template_id} ] \n ")

     # TODO add more action_node

    def end(self):
        print("Flow ended for current profile.")


# Load JSON from file
def load_json_file(file_path):
    """
    Load JSON data from a file, ensuring the file exists and is not empty.

    :param file_path: Path to the JSON file
    :return: Parsed JSON data as a dictionary
    :raises FileNotFoundError: If the file does not exist
    :raises ValueError: If the file is empty or contains invalid JSON
    """
    # Check if the file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check if the file is not empty
    if os.path.getsize(file_path) == 0:
        raise ValueError(f"The file is empty: {file_path}")

    # Read and parse the JSON file
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file {file_path}: {e}")


def run_data_automation(json_file_path: str):
    flowchart_json = ''
    try:
        flowchart_json = load_json_file(json_file_path)
        print("JSON loaded successfully:", flowchart_json)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")

    # Test profiles
    profiles = [
        {"birthday": "1991-11-25", "name": "John Doe"},
        {"birthday": "1999-12-01", "name": "Jane Smith"},
        {"birthday": "1986-11-25", "name": "Peter Pane"}
    ]

    if flowchart_json != '':
        # Run the engine

        engine = AutomationEngine(flowchart_json)

        # Process all profiles
        for profile in profiles:
            context = Context(profile)
            engine.run(context)
    else:
        print(f"Error: flowchart_json is empty ")


# Test JSON file path (ensure this file contains the provided flowchart JSON)
json_file_path = "./data/flowchart_birthday.json"
run_data_automation(json_file_path)
