from typing import List, Dict, Any
import networkx as nx

class TaskPrioritizer:
    def __init__(self):
        # Initialize any necessary attributes here
        pass

    def prioritize(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Convert priority to a numerical value
        priority_mapping = {'low': 0.3, 'medium': 0.5, 'high': 0.7}
        task['priority'] = priority_mapping.get(task.get('priority', 'medium'), 0.5)
        return task

    def prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        G = nx.DiGraph()
        
        for task in tasks:
            G.add_node(task['id'], task=task)
            for dep in task.get('dependencies', []):
                G.add_edge(dep, task['id'])
        
        try:
            ordered_tasks = list(nx.topological_sort(G))
        except nx.NetworkXUnfeasible:
            # Handle cycles in the dependency graph
            ordered_tasks = list(G.nodes())
        
        prioritized_tasks = []
        for task_id in ordered_tasks:
            task = G.nodes[task_id]['task']
            priority = self._calculate_priority(task, G)
            task['priority'] = priority
            prioritized_tasks.append(task)
        
        return sorted(prioritized_tasks, key=lambda x: x['priority'], reverse=True)

    def _calculate_priority(self, task: Dict[str, Any], G: nx.DiGraph) -> float:
        importance = task.get('importance', 1)
        urgency = task.get('urgency', 1)
        num_dependents = len(list(G.successors(task['id'])))
        
        return importance * urgency * (1 + 0.1 * num_dependents)