# -*- coding: utf-8 -*-
import yurlungur
from yurlungur.core import app, env


class MetaObject(type):
    def __new__(cls, name, bases, attrs):
        return super(MetaObject, cls).__new__(cls, name, bases, attrs)


class MetaAttr(type):
    def __new__(cls, name, bases, attrs):
        return super(MetaAttr, cls).__new__(cls, name, bases, attrs)


class YMObject(object):
    """command wrapper for any application"""
    if env.Substance():
        from yurlungur.adapters import substance as sd
        graph = sd.graph
        manager = sd.manager

    if env.Davinci():
        resolve = env.__import__("DaVinciResolveScript").scriptapp("Resolve")
        if resolve:
            fusion = resolve.Fusion()
            manager = resolve.GetProjectManager()

    if env.Unreal():
        from yurlungur.adapters import ue4
        editor = ue4.EditorUtil()
        assets = ue4.GetEditorAssetLibrary()
        levels = ue4.GetEditorLevelLibrary()
        tools = ue4.tools

    if env.Photoshop():
        from yurlungur.adapters import photoshop as ps
        doc = ps.Document()._doc

    def __getattr__(self, item):
        try:
            from inspect import getmembers
        except ImportError:
            setattr(yurlungur, item, getattr(app.application, item))
            return getattr(app.application, item)

        for cmd, _ in getmembers(app.application):
            if cmd == item:
                setattr(
                    yurlungur, cmd,
                    (lambda str: dict(getmembers(app.application))[str])(cmd)
                )
                return getattr(yurlungur, item)

        return getattr(yurlungur, item, False)

    def eval(self, script):
        if env.Maya():
            import maya.mel as mel
            return mel.eval(script)
        if env.Houdini():
            return app.application.hscript(script)
        if env.Max():
            import MaxPlus
            return MaxPlus.Core.EvalMAXScript(script)
        if env.Davinci() and self.resolve:
            self.fusion.GetCurrentComp().Execute(script)
        if env.Photoshop():
            return app.application.DoJavascript(script)

    @property
    def module(self):
        return app.application


# Dynamic Class
_YObject = MetaObject("YObject", (object,), {"__doc__": MetaObject.__doc__})
_YAttr = MetaAttr("YAttr", (object,), {"__doc__": MetaAttr.__doc__})
_YVector = _YMatrix = _YColors = OM = object

if env.Maya():
    import maya.api.OpenMaya as OM

    _YVector = type('_YVector', (OM.MVector,), dict())
    _YMatrix = type('_YMatrix', (OM.MMatrix,), dict())
    _YColors = type('_YColors', (OM.MColor,), dict())

    from yurlungur.tool.meta import meta

    if hasattr(meta, "loadPlugin"):
        for plugin in "fbxmaya.mll", "AbcImport.mll", "AbcExport.mll":
            meta.loadPlugin(plugin, qt=1)

elif env.Houdini() or env.Unreal():
    from yurlungur.tool.meta import meta

    _YVector = type('_YVector', (
        meta.Vector if hasattr(meta, "Vector") else meta.Vector3,
    ), dict())

    _YMatrix = type('_YMatrix', (
        meta.Matrix if hasattr(meta, "Matrix") else meta.Matrix4,
    ), dict())

    _YColors = type('_YColors', (meta.Color,), dict())

elif env.Blender():
    import mathutils

    _YVector = type('_YVector', (mathutils.Vector,), dict())
    _YMatrix = type('_YMatrix', (mathutils.Matrix,), dict())
    _YColors = type('_YColors', (mathutils.Color,), dict())

elif env.Substance():
    from yurlungur.tool.meta import meta
    # _YVector = type('_YVector', (meta.SDValueVector,), dict())
    # _YMatrix = type('_YMatrix', (meta.SDValueMatrix,), dict())
    # _YColor = type('_YColors', (meta.SDValueColorRGBA,), dict())

elif env.Nuke():
    import _nukemath

    _YVector = type('_YVector', (_nukemath.Vector3,), dict())
    _YMatrix = type('_YMatrix', (_nukemath.Matrix4,), dict())

elif env.Max():
    import MaxPlus

    _YVector = type('_YVector', (MaxPlus.Point3,), dict())
    _YMatrix = type('_YMatrix', (MaxPlus.Matrix3,), dict())
    _YColors = type('_YColors', (MaxPlus.Color,), dict())
