import simpy

class Constructor():
    """
    Simulates the Constructor building.

    Parameters:
        env: The simpy.Environment
        out_rate: Number of items per min produced
        recipe: Dictionary with keys of [in, out], values equal to 
            the recipe of the produced item
    """

    def __init__(self, env : simpy.Environment, 
        out_rate : float, recipe:dict, in_max:int, out_max:int,
        in_stream, out_stream = None):
        self.env = env
        self.in_stream = in_stream
        self.out_stream = out_stream
        self.action = env.process(self.run())
        self.recipe = recipe
        self.produce_duration = self.recipe["out"]/out_rate

        self.input_stack = simpy.Container(env, capacity = in_max)
        self.output_stack = simpy.Container(env, capacity = out_max)


    def run(self):
        while True:
            can_craft = (
                (self.input_stack.level > self.recipe["in"])
                and (
                    (self.output_stack.level + self.recipe["out"])
                    < self.output_stack.capacity
                )
            )
            
            if can_craft:
                yield self.produce()
            

    def produce(self):
        yield self.env.timeout(self.produce_duration)