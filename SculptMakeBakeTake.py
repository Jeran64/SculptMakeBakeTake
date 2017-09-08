bl_info = {
    "name": "SculptScript",
    "description": "Make primitives that can be edited and baked into 2d colored images, which can also be imported. Color to space visualizer",
    "author": "Jeran Halfpap   ",
    "version": (0, 9, 0),
    "blender": (2, 70, 0),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

import bpy,bmesh
import math
print("starting :D")
Width=32#misnomer names. these are the x and y values, but also are used to refer to the images
Height=32
shape="S"#[C]ylinder [S]phere [P]lane Pi[L]low

#https://blender.stackexchange.com/questions/8221/how-can-i-add-uv-coords-to-a-mesh-from-script
#https://blender.stackexchange.com/questions/2407/how-to-create-a-mesh-programmatically-without-bmesh
#http://blenderscripting.blogspot.com/2011/06/using-frompydata.html
#bpy.ops.object.mode_set(mode='EDIT')
#https://blender.stackexchange.com/questions/9399/add-uv-layer-to-mesh-add-uv-coords-with-python
#http://web.purplefrog.com/~thoth/blender/python-cookbook/barber-pole.html
#https://blender.stackexchange.com/questions/3673/why-is-accessing-image-data-so-slow/3678#3678
#https://blender.stackexchange.com/questions/15890/is-it-possible-to-edit-images-programmatically-with-the-blender-api
#https://blender.stackexchange.com/questions/57306/how-to-create-a-custom-ui
#https://blender.stackexchange.com/questions/100/how-do-i-completely-remove-an-image-from-my-blend-file
#https://stackoverflow.com/questions/4405787/generating-vertices-for-a-sphere
#define the mesh object that we will be working with.
##############################################################
#_________________make_______________________________________#
##############################################################
def sculptMake(datapoints):
    global Width
    global Height
    print("Making a sculpt of width: "+ str(Width)+" and height: "+str(Height))
    mySculptMesh = bpy.data.meshes.new("Sculptie")

    #these are the lists that we will be adding the vert points to.
    myVerts=[]
    #this is where we will define edges by referring to point sin our list of verts.
    myEdges=[]
    #this is where we define quads by giving a list of 4 verts from our vert list.
    myFaces=[]

    ######################################loop through our height and width to define a grid of points.
    deltaTheta=math.pi/(Height) #subtract 1 to account for poles.
    deltaPhi=(math.pi*2)/Width#precalculate our division
    theta=0
    phi=0
    if (datapoints==[]): #if data point sis null, then that means we didnt define it first, this means create a whole new bunch!
        if(shape=="S"):#sphere
            for ring in range(0,Height):
                theta=theta+deltaTheta
                for point in range(0,Width):
                    phi=phi+deltaPhi
                    myVerts.append((math.sin(theta)*math.cos(phi),math.sin(theta)*math.sin(phi),math.cos(theta)))#use math to plot a UV Sphere
        elif(shape=="L"):#pillow
            
            for y in range(Height):
                for x in range(Width):
                    #myVerts.append((math.cos(XPIESLICE*y),math.sin(YPIESLICE*y)*math.sin(XPIESLICE*x),math.cos(YPIESLICE*y)))
                    myVerts.append((math.cos(math.pi*2*(x/Width)),math.sin(math.pi*2*(x/Width))*math.sin(math.pi*(y/Height)),math.cos(math.pi*(y/Height))))#
        elif(shape=="C"):#cylinder
            for y in range(Height):
                for x in range(Width):
                    myVerts.append((math.cos(math.pi*2*(x/Width)),math.sin(math.pi*2*(x/Width)),y/Height))#use math to plot a circle, and then space it vertically by a linear value.
        else:#assume that shape =="p". this will catch malformed inputs and default them to plane.
            for y in range(Height): 
                for x in range(Width):
                    #myVerts.append((x-(Width/2),y-(Height/2),0)) #centered version
                    myVerts.append((x/Width,y/Height,0))    #non bounding box version
    else:
        myVerts=datapoints#this means that our data points and shape were defined using the sculpt take function, and that we should use that data instead.
            
    #loop through our list of verts and define our faces
    for y in range(Height-1):
        for x in range(Width-1):
            rPoint=x+(y*Width) #Reference Point. we need to looop through just about most of the points in the list of points. This will convert our x,y coordinates into the linear numberd list.
            myFaces.append([rPoint,rPoint+1,rPoint+1+Width,rPoint+Width])#we add width, which is equal the linear value of the next row of points.
            #wprint ("working face: ")
            #print (x,y,rPoint,rPoint+1,rPoint+1+Width,rPoint+Width)
            
    #build the mesh
    mySculptMesh.from_pydata(myVerts,myEdges,myFaces)
    mySculptMesh.update()

    #add the mesh to an object in the scene
    mySculptObject=bpy.data.objects.new("Sculpty",mySculptMesh)
    mySculptObject.data=mySculptMesh

    #not sure what this does yet. but im pretty sure that it adds it to the scene.
    scene=bpy.context.scene
    scene.objects.link(mySculptObject)
    mySculptObject.select=True

    print ("Finished. Your sculptie is ready to be manipulated.")
##############################################################
#____________________take____________________________________#
##############################################################
def sculptTake(filename):       
    global Width
    global Height
    image=bpy.data.images[filename]#look for an image in our loadout of this name. we will target it.
    Width=image.size[0] #because we have loaded an image, overwrite our values that deal with the nature of our sizes.
    Height=image.size[1]
    print("loading a sculpt of width: "+ str(Width)+" and height: "+str(Height))
    def get_pixel(img,x,y):
        color=[]
        offs = (x + y*Width) * 4
        for i in range(4):
            color.append( image.pixels[offs+i] )
        return color
    #loop throught he pixels in the image and define a list of verticies.
    pointList=[]#make a temporary list to stuff our points into.
    for y in range(Height): 
        for x in range(Width):
            ourColor=get_pixel(image,x,y)
            pointList.append([ourColor[0],ourColor[1],ourColor[2]]) 
    sculptMake(pointList)   
    print ("Finished. Your sculptie is imported.")

##############################################################
#_____________________bake___________________________________#
##############################################################    
def sculptBake(filename):
    selectedObject=bpy.context.selected_objects[0]#we only want the first item in this list of selected items
    if selectedObject.type=="MESH":
        workingObject=selectedObject.data#rejigger the working data to the mesh layer.
        workingObject.uv_textures.new("sculptUV")
        bm = bmesh.new()
        bm.from_mesh(workingObject)
    else:
        print("Incorrect Object type selected.")

    #access the verts of the object
    vert_list=[vertex.co for vertex in workingObject.vertices]

    ###create the bounding box for the sculpt. This will normalize it.
    minR=100
    minG=100
    minB=100
    maxR=-100 #define a suitably large size.
    maxG=-100
    maxB=-100

    for i in range(0,len(vert_list)):
        #min
        if vert_list[i][0]<minR:#red
            minR=vert_list[i][0]
        if vert_list[i][1]<minG:#green
            minG=vert_list[i][1]
        if vert_list[i][2]<minB:#blue
            minB=vert_list[i][2]
        #max
        if vert_list[i][0]>maxR:#red
            maxR=vert_list[i][0]
        if vert_list[i][1]>maxG:#green
            maxG=vert_list[i][1]
        if vert_list[i][2]>maxB:#blue
            maxB=vert_list[i][2]

    print("Bounding box is")
    print(minR,minG,minB,maxR,maxG,maxB)
    ###assign image.
    #sculptMap=bpy.ops.image.new(name='sculptMap',width=Width,height=Height)
    sculptMap=bpy.data.images.new(name=filename,width=Width,height=Height)

    workingPixels=list(sculptMap.pixels)#save an editiable copy of the pixels. that way we can quickly edit the image.

    #bake image.
    for i in range(0, len(workingPixels),4):
        workingPixels[i+0] = (((vert_list[int(i/4)][0])-minR)/(maxR-minR))#red channel
        workingPixels[i+1] = (((vert_list[int(i/4)][1])-minG)/(maxG-minG))#green channel
        workingPixels[i+2] = (((vert_list[int(i/4)][2])-minB)/(maxB-minB))#blue channel        
        
    #write image from pixel buffer to the actual bits
    sculptMap.pixels[:]=workingPixels

    #update image
    sculptMap.update()

    print ("Finished. Your sculpt map is rendered.")
##############################################################
#_______________________interface stuff______________________#
##############################################################

import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       )


# ------------------------------------------------------------------------
#    store properties in the active scene
# ------------------------------------------------------------------------

class MySettings(PropertyGroup):

    my_width = IntProperty(
        name = "X Value",
        description="A integer property",
        default = 32,
        min = 2,
        max = 1024
        )
    my_height = IntProperty(
        name = "Y Value",
        description="A integer property",
        default = 32,
        min = 2,
        max = 1024
        )
    my_string = StringProperty(
        name="filename",
        description=":",
        default="Untitled",
        maxlen=1024,
        )
    my_enum = EnumProperty(
        name="Dropdown:",
        description="Apply Data to attribute.",
        items=[ ('C', "Cylinder", ""),
                ('S', "Sphere", ""),
                ('L', "Pillow", ""),
                ('P', "Plane", ""),
               ]
        )
# ------------------------------------------------------------------------
#    operators
# ------------------------------------------------------------------------

class MAKEOperator(bpy.types.Operator):
    bl_idname = "wm.make"
    bl_label = "make"

    def execute(self, context):
        global Width
        global Height
        global shape
        scene = context.scene
        mytool = scene.my_tool

        # save the values 
        Width=mytool.my_width
        Height=mytool.my_height
        shape=mytool.my_enum
        print(Width, Height)
        print("enum state:", mytool.my_enum)
        #execute funtion
        sculptMake([])
        return {'FINISHED'}
    
class BAKEOperator(bpy.types.Operator):
    bl_idname = "wm.bake"
    bl_label = "bake"

    def execute(self, context):
        global Width
        global Height
        scene = context.scene
        mytool = scene.my_tool

        # save the values 
        Width=mytool.my_width
        Height=mytool.my_height
        sculptBake(mytool.my_string)
        return {'FINISHED'}
    
class TAKEOperator(bpy.types.Operator):
    bl_idname = "wm.take"
    bl_label = "take"

    def execute(self, context):
        global Width
        global Height
        scene = context.scene
        mytool = scene.my_tool

        # print the values to the console
        Width=mytool.my_width
        Height=mytool.my_height
        print("string value:", mytool.my_string, "Height",Height)
        sculptTake(mytool.my_string)
        return {'FINISHED'}

# ------------------------------------------------------------------------
#    my tool in objectmode
# ------------------------------------------------------------------------

#give blender information about the context of the interface
class OBJECT_PT_my_panel(Panel):
    bl_idname = "OBJECT_PT_my_panel"
    bl_label = "My Panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "TOOLS"    
    bl_category = "Tools"
    bl_context = "objectmode"   

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.prop(mytool, "my_width")#add the buttons to the interface. refer to them by the variable name.
        layout.prop(mytool, "my_height")
        layout.prop(mytool, "my_string")
        layout.prop(mytool,"my_enum", text="")
        layout.operator("wm.make")
        layout.operator("wm.bake")
        layout.operator("wm.take")
        

# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.my_tool = PointerProperty(type=MySettings)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()
