from typing import List, Set, Callable, Self
from abc import abstractmethod, ABC

class State(ABC):
    # It would make sense to declare __hash__ as an @abstractmethod too, in order to force an error at
    # instantiation as when one of the other abstract methods are undefined.
    # However, the class implements a default __hash__ method, so it will not give an error at instantiation.
    # However however, the default __hash__ function goes away when __eq__ is defined as the two methods
    # need to be aligned, i.e., when a == b, then hash(a) must be equal to hash(b).
    # Still, you do get an error, when you try to use the object where the __hash__ is needed, e.g., as a key
    # for a dict or a set.
    @abstractmethod
    def children(self) -> List[Self]:
        ...
    @abstractmethod
    def __eq__(self, other):
        ...

def bfs(initial_state: State, end_state: Callable[[State], bool]) -> List[State]:
    if initial_state is None:
        return []
    visited = set()
    path = [initial_state]
    queue = [ (initial_state, path) ]
    while len(queue) > 0:
        (state, path) = queue.pop(0)
        # print(f"state={state}  ", end="")
        # print_list(path, "path")
        visited.add(state)
        for child in state.children():
            if end_state(child):
                print()
                print("states visited:", len(visited))
                return path + [child]
            if child not in visited:
                visited.add(child)
                # append to end of the queue to achieve breadth-first search
                queue.append( (child, path + [child]) )
        # print_list([sp for (sp,_) in queue], "queue")
    print("end state not found")
    print("states visited:", len(visited))
    return([])

