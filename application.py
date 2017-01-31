from PyQt4 import QtCore, QtGui, uic
import sys
import icons_rc


class Node(object):
    '''Base class for nodes in the custom tool library data model'''

    def __init__(self, name, parent=None):

        self._name = name
        self._children = []
        self._parent = parent

        if parent is not None:
            parent.addChild(self)

    def typeInfo(self):
        '''returns the type of node'''
        return "NODE"

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):

        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):

        if position < 0 or position > len(self._children):
            return False

        child = self._children.pop(position)
        child._parent = None

        return True

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def child(self, row):
        return self._children[row]

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)


class ToolNode(Node):
    '''Tool represents the machining tool with all properties'''

    def __init__(self, name, parent=None):
        super(ToolNode, self).__init__(name, parent)

        self._toolType = 'EndMill'
        self._material = 'Carbide'
        self._diameter = 6.35
        self._lengthOffset = 0.0
        self._flatRadius = 0.0
        self._cornerRadius = 0.0
        self._cuttingEdgeAngle = 90.0
        self._cuttingEdgeHeight = 10.0

    def toolType(self):
        '''distinguishes an endmill from a drill bit, for example'''
        return self._toolType

    def toolMaterial(self):
        '''indicates the material type.  Carbide vs HSS, for example'''
        return self._material

    def toolDiameter(self):
        '''Diameter of the overall tool at the cutting edge'''
        return self._diameter

    def lengthOffset(self):
        return self._lengthOffset

    def flatRadius(self):
        return self._flatRadius

    def cornerRadius(self):
        return self._cornerRadius

    def cuttingEdgeAngle(self):
        return self._cuttingEdgeAngle

    def cuttingEdgeHeight(self):
        return self._cuttingEdgeHeight

    def setToolType(self, tooltype):
        self._toolType = tooltype

    def setToolMaterial(self, material):
        self._material = material

    def setToolDiameter(self, diameter):
        self._diameter = diameter

    def setLengthOffset(self, lengthOffset):
        self._lengthOffset = lengthOffset

    def setFlatRadius(self, flatRadius):
        self._flatRadius = flatRadius

    def setCornerRadius(self, cornerRadius):
        self._cornerRadius = cornerRadius

    def setCuttingEdgeAngle(self, CuttingEdgeAngle):
        self._cuttingEdgeAngle = CuttingEdgeAngle

    def setCuttingEdgeHeight(self, CuttingEdgeHeight):
        self._cuttingEdgeHeight = CuttingEdgeHeight

    def typeInfo(self):
        return "TOOL"


class ListNode(Node):
    '''represents a list of tools to be operated on together'''

    def __init__(self, name, parent=None):
        super(ListNode, self).__init__(name, parent)

    def typeInfo(self):
        return "LIST"


class DocumentNode(Node):
    '''represents and open document in FreeCAD'''

    def __init__(self, name, parent=None):
        super(DocumentNode, self).__init__(name, parent)

    def typeInfo(self):
        return "DOCUMENT"


class JobNode(Node):
    '''represents a job in an open document in FreeCAD'''
    def __init__(self, name, parent=None):
        super(JobNode, self).__init__(name, parent)

    def typeInfo(self):
        return "JOB"


class LibraryModel(QtCore.QAbstractItemModel):
    '''Base class of the custom data model'''
    filterRole = QtCore.Qt.UserRole

    def __init__(self, root, parent=None):
        super(LibraryModel, self).__init__(parent)
        self._rootNode = root

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent):
        return 9

    def data(self, index, role):
        if not index.isValid():
            return None

        node = index.internalPointer()
        typeInfo = node.typeInfo()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return node.name()

            if typeInfo == "TOOL":
                if index.column() == 1:
                    return node.toolType()
                if index.column() == 2:
                    return node.toolMaterial()
                if index.column() == 3:
                    return node.toolDiameter()
                if index.column() == 4:
                    return node.lengthOffset()
                if index.column() == 5:
                    return node.flatRadius()
                if index.column() == 6:
                    return node.cornerRadius()
                if index.column() == 7:
                    return node.cuttingEdgeAngle()
                if index.column() == 8:
                    return node.cuttingEdgeHeight()

        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:

                if typeInfo == "TOOL":
                    return QtGui.QIcon(QtGui.QPixmap(":/Light.png"))

                if typeInfo == "LIST":
                    return QtGui.QIcon(QtGui.QPixmap(":/Transform.png"))

                if typeInfo == "DOCUMENT":
                    return QtGui.QIcon(QtGui.QPixmap(":/Camera.png"))

                if typeInfo == "JOB":
                    return QtGui.QIcon(QtGui.QPixmap(":/Camera.png"))

        if role == LibraryModel.filterRole:
            return node.typeInfo()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        print "in setData"
        if index.isValid():
            node = index.internalPointer()

            if role == QtCore.Qt.EditRole:

                node.setName(value)
                self.dataChanged.emit(index, index)

                return True
        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Library"
            elif section == 1:
                return "Tool Type"
            elif section == 2:
                return "Material"
            elif section == 3:
                return "Diameter"
            elif section == 4:
                return "LengthOffset"
            elif section == 5:
                return "Flat Radius"
            elif section == 6:
                return "Corner Radius"
            elif section == 7:
                return "Cutting Edge Angle"
            elif section == 8:
                return "Cutting Edge Height"

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def parent(self, index):
        node = self.getNode(index)
        parentNode = node.parent()

        if parentNode == self._rootNode:
            return QtCore.QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parent):
        parentNode = self.getNode(parent)
        childItem = parentNode.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._rootNode

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode = self.getNode(parent)

        self.beginInsertRows(parent, position, position + rows - 1)

        for row in range(rows):

            childCount = parentNode.childCount()
            childNode = Node("untitled" + str(childCount))
            success = parentNode.insertChild(position, childNode)

        self.endInsertRows()

        return success

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)

        for row in range(rows):
            success = parentNode.removeChild(position)

        self.endRemoveRows()

        return success

base, form = uic.loadUiType("Views/ToolLibrary.ui")
tooleditBase, tooleditForm = uic.loadUiType("Views/ToolEdit.ui") 
toollistBase, toollistForm = uic.loadUiType("Views/ToolList.ui") 
propEditorBase, propEditorForm = uic.loadUiType("Views/PropertyEditor.ui")


class PropertyEditorPanel(propEditorBase,propEditorForm):
    '''Container for the list and details editor panels.  Switches based on type of node'''
    def __init__(self, parent=None):
        super(propEditorBase, self).__init__(parent)
        self.setupUi(self)

        self._proxyModel = None
        self._model = None

        self._tooleditor = ToolEditPanel(self)
        self._toollist = ToolListPanel(self)

        self.layoutProperties.addWidget(self._tooleditor)
        self.layoutProperties.addWidget(self._toollist)

        self._tooleditor.setVisible(False)
        self._toollist.setVisible(False)

    def setModel(self, proxyModel):
        self._model = proxyModel.sourceModel
        self._proxyModel = proxyModel

        self._tooleditor.setModel(proxyModel)
        self._toollist.setModel(proxyModel)

    def setSelection(self, current, old):
        self._tooleditor.setSelection(current)
        self._toollist.setSelection(current)
        current = self._proxyModel.mapToSource(current)

        node = current.internalPointer()
        if node is not None:
            typeinfo = node.typeInfo()

        if typeinfo in ["LIST", "JOB"]:
            self._tooleditor.setVisible(False)
            self._toollist.setVisible(True)

            # parent = current.parent()
            # print parent
            # self._dataMapper.setRootIndex(parent)
            # self._dataMapper.setCurrentModelIndex(current)

        elif typeinfo == "TOOL":
            self._tooleditor.setVisible(True)
            self._toollist.setVisible(False)

        elif typeinfo == "DOCUMENT":
            self._tooleditor.setVisible(False)
            self._toollist.setVisible(False)
        else:
            pass



class ToolEditPanel(tooleditBase,tooleditForm):
    '''editor for tool details'''
    def __init__(self, parent=None):
        super(tooleditBase, self).__init__(parent)
        self.setupUi(self)
        self._proxyModel = None
        self._dataMapper = QtGui.QDataWidgetMapper()
        # self._typeDelegate = QtGui.QItemDelegate()
        # self._typeDelegate.
        self.uiToolType.currentIndexChanged.connect(self._setTypeCombo)
        self.uiHiddenType.editingFinished.connect(self._setTypeCombo)

    def setModel(self, proxyModel):
        print "setting tooleditpanel model"
        self._proxyModel = proxyModel

        print ("setting datamapper to: {}".format(proxyModel.sourceModel()))

        self._dataMapper.setModel(proxyModel.sourceModel())
        self._dataMapper.addMapping(self.uiName, 0)
        #self._dataMapper.addMapping(self.uiToolType, 1)
        self._dataMapper.addMapping(self.uiHiddenType, 1)
        
        #self._dataMapper.addMapping(self.uiMaterial, 2)
        self._dataMapper.addMapping(self.uiHiddenMaterial, 2)
        self._dataMapper.addMapping(self.uiDiameter, 3)
        self._dataMapper.addMapping(self.uiLengthOffset, 4)
        self._dataMapper.addMapping(self.uiFlatRadius, 5)
        self._dataMapper.addMapping(self.uiCornerRadius, 6)
        self._dataMapper.addMapping(self.uiCuttingEdgeAngle, 7)
        self._dataMapper.addMapping(self.uiCuttingEdgeHeight, 8)


    def _setTypeCombo(self):
        tt = str(self.uiHiddenType.text())
        tt = self.uiToolType.currentIndex()
        ttstring = self.getType(tt)
        self.uiHiddenType.setText(ttstring)
        #print "made it {}: {}".format(tt, self.getType(tt))

    def setSelection(self, current):
        print 'setting item selection'
        current = self._proxyModel.mapToSource(current)
        print current
        parent = current.parent()
        # print parent
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)

    def getType(self, tooltype):
        print tooltype
        "gets a combobox index number for a given type or viceversa"
        toolslist = ["Drill", "CenterDrill", "CounterSink", "CounterBore",
                     "Reamer", "Tap", "EndMill", "SlotCutter", "BallEndMill",
                     "ChamferMill", "CornerRound", "Engraver"]
        if isinstance(tooltype, str):
            if tooltype in toolslist:
                return toolslist.index(tooltype)
            else:
                return 0
        else:
            return toolslist[tooltype]

    def getMaterial(self, material):
        "gets a combobox index number for a given material or viceversa"
        matslist = ["HighSpeedSteel", "HighCarbonToolSteel", "CastAlloy",
                    "Carbide", "Ceramics", "Diamond", "Sialon"]
        if isinstance(material, str):
            if material in matslist:
                return matslist.index(material)
            else:
                return 0
        else:
            return matslist[material]

class ToolListPanel(toollistBase,toollistForm):
    '''List panel.  Shows the grid of tools in a list'''
    def __init__(self, parent=None):
        super(toollistBase, self).__init__(parent)
        self.setupUi(self)

    def setModel(self, proxyModel):
        self._model = proxyModel.sourceModel()
        self._proxymodel = proxyModel
        self.uiToolList.setModel(proxyModel)

    def setSelection(self, current):
        print 'setting list selection'
        print current
        self.uiToolList.setRootIndex(current)

class EditorPanel(base,form):
    def __init__(self, parent=None):
        super(base, self).__init__(parent)
        self.setupUi(self)

        rootNode = Node("Library")
        cn0 = ListNode("Library", rootNode)
        cn1 = ToolNode("1/4 inch cutter", cn0)
        cn2 = ToolNode("Face mill", cn0)
        cn2.setToolDiameter(50.0)
        cn2.setToolMaterial("HighSpeedSteel")
        cn3 = ListNode("Plastic Tools", cn0)
        cn4 = ToolNode("5mm Drill", cn3)
        cn4.setToolType("CenterDrill")
        cn5 = ToolNode("3mm endmill", cn3)
        cn6 = DocumentNode("document thing", rootNode)
        cn7 = JobNode("Job", cn6)
        cn8 = ToolNode("1/4 inch cutter", cn7)

        self._model = LibraryModel(rootNode)

        self._proxyModel = QtGui.QSortFilterProxyModel()
        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setFilterRole(LibraryModel.filterRole)
        #filterstring = 'LIST|DOCUMENT'
        #self._proxyModel.setFilterRegExp(filterstring)

        self.libraryList.setModel(self._proxyModel)

        #hide all the data columns in the treeview
        for i in range(self._proxyModel.columnCount()-1):
            self.libraryList.hideColumn(i+1)

        self._propEditor = PropertyEditorPanel(self)
        self._propEditor.setModel(self._proxyModel)

        self.layoutDetails.addWidget(self._propEditor)

        QtCore.QObject.connect(self.libraryList.selectionModel(), QtCore.SIGNAL("currentChanged(QModelIndex, QModelIndex)"), self._propEditor.setSelection)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setStyle("plastique")

    wnd = EditorPanel()
    wnd.show()

    sys.exit(app.exec_())
