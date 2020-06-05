from spade.message import Message
from spade.template import Template

class Event():
    def __init__(self, name, data, autofire = True):
        self.name = name
        self.data = data
        if autofire:
            self.fire()
    def fire(self):
        for observer in Observer._observers:
            if self.name in observer._observables:
                observer._observables[self.name](self.data)

class Observer():
    _observers = []
    def __init__(self):
        self._observers.append(self)
        self._observables = {}
    def observe(self, event_name, callback):
        self._observables[event_name] = callback


def make_message(template: Template, **kwargs) -> Message:
    def from_template_or_kwargs(attrname):
        try:
            return kwargs[attrname]
        except KeyError:
            return getattr(template, attrname, None)

    return Message(
        sender=from_template_or_kwargs('sender'),
        to=from_template_or_kwargs('to'),
        body=from_template_or_kwargs('body'),
        thread=from_template_or_kwargs('thread'),
        metadata=from_template_or_kwargs('metadata')
    )

def make_metadata_template(performative: str, ontology: str) -> Template:
    return Template(metadata=dict(
        performative=performative,
        ontology=ontology
    ))