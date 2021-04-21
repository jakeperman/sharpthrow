class LocalDebugger:
    def __init__(self):
        self.enabled = True

    def out(self, variable, value):
        if self.enabled:
            output = f"{variable}: {value}"
            print(output)
            return output

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True


class Debugger:
    def __init__(self, class_name):
        self.c_name = class_name
        self.enabled = True

    def out(self, variable):
        if self.enabled:
            vars = self.get_vars()
            var_name = variable
            var_val = vars[variable]
            output = f"{var_name}: {var_val}"
            print(output)
            return output

    def get_vars(self):
        return self.c_name.__dict__

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True