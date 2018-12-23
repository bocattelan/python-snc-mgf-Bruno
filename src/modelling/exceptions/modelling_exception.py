from tokenize import String


class ModellingError(Exception):
    message: String
    pass


class PathError(ModellingError):

    def __init__(self, path, message: String):
        self.path = path
        self.message = message

    pass


class LinkError(ModellingError):

    def __init__(self, src, dst, message: String):
        self.src = src
        self.dst = dst
        self.message = message

    pass


class FlowCreationError(ModellingError):

    def __init__(self, message: String):
        self.message = message

    pass


class FlowError(ModellingError):

    def __init__(self, flow, message: String):
        self.flow = flow
        self.message = message

    pass
