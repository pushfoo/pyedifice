import contextlib
import inspect
import logging
import queue
import time
import traceback
import typing as tp

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtRemoveInputHook, pyqtRestoreInputHook

from .component import Component, PropsDict, register_props, BaseComponent, RootComponent
from .base_components import WindowManager
from .engine import RenderEngine
from .utilities import set_trace


class App(object):

    def __init__(self, component: Component, title: tp.Text = "Edifice App"):
        self.app = QtWidgets.QApplication([])


        rendered_component = component.render()
        if isinstance(rendered_component, RootComponent):
            self._root = RootComponent()(component)
        else:
            self._root = WindowManager()(component)
        self._render_engine = RenderEngine(self._root, self)

        self._title = title

        # Support for reloading on file change
        self._file_change_rerender_event_type = QtCore.QEvent.registerEventType()

        class EventReceiverWidget(QtWidgets.QWidget):
            def event(_self, e):
                if e.type() == self._file_change_rerender_event_type:
                    e.accept()
                    while not self._class_rerender_queue.empty():
                        file_name, classes = self._class_rerender_queue.get_nowait()
                        try:
                            ret = self._render_engine._refresh_by_class(classes)
                        except Exception as e:
                            logging.warn("Encountered exception while reloading: %s" % e)
                            self._class_rerender_response_queue.put_nowait(False)
                            traceback.print_exc()
                            continue

                        for _, (_, commands) in ret:
                            for command in commands:
                                command[0](*command[1:])
                        self._class_rerender_queue.task_done()
                        self._class_rerender_response_queue.put_nowait(True)
                        logging.info("Rerendering Components in %s due to source change", file_name)
                    return True
                else:
                    return super().event(e)

        self._event_receiver = EventReceiverWidget()
        self._class_rerender_queue = queue.Queue()
        self._class_rerender_response_queue = queue.Queue()

    def _request_rerender(self, components, newprops, newstate, execute=True):
        ret = self._render_engine._request_rerender(components, newprops, newstate)
        for _, (_, commands) in ret:
            for command in commands:
                command[0](*command[1:])

    def start(self):
        self._request_rerender([self._root], {}, {})
        self.app.exec_()
