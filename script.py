import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):

    name = ''
    num_frames = 1

    vary_found = False
    for command in commands:
        if command['op'] == 'basename':
            name = command['args'][0]
        elif command['op'] == 'frames':
            num_frames = int(command['args'][0])
        elif command['op'] == 'vary':
            vary_found = True
    if vary_found and num_frames == 1:
        print("Number of frames need to specified")
        return

    return (name, num_frames)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def makecoolknobs(startval,endval,start_frame,end_frame,rate):
    tl = []
    if (rate == 1):
        step = (endval-startval)/(end_frame-start_frame)
        tl = [startval+step*i for i in range(0,end_frame-start_frame)] # num_frames = end_frame-start_frame-1
    else:
        diff = endval - startval
        if (startval == 0):
            newstart = .01
        else:
            newstart = startval
        def tfunc(start,end,f1,f2,currstep):
            return start * (end/start)**((currstep-f1)/(f1-f2))
        tl = [tfunc(startval,endval,start_frame,end_frame,i) for i in range(start_frame,end_frame)]
    return tl

def second_pass( commands, num_frames ):
    frames = [ {} for i in range(num_frames) ]

    for command in commands:
        print(command)
        if command['op'] == 'vary':
            knob = command['knob']

            start_frame = command['args'][0]
            end_frame = command['args'][1]

            val = command['args'][2]
            # this line
            print(command['args'])
            if (len(command['args']) > 4):
                rate = int(command['args'][4])
            else:
                rate = 1
            valsforframes = makecoolknobs(int(val),int(command['args'][3]),int(start_frame),int(end_frame),rate)
            for ind in range(int(start_frame),int(end_frame)):
                frames[ind][knob] = valsforframes[ind-int(start_frame)]

            '''step =  (command['args'][3] - command['args'][2]) / (end_frame - start_frame)
            for index in range(int(start_frame),int(end_frame)):
                frames[index][knob] = val
                val += step'''
    return frames

def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print ("Parsing failed.")
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)


    tmp = new_matrix()
    ident( tmp )

    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    zbuffer = new_zbuffer()
    tmp = []
    step_3d = 100
    consts = ''
    coords = []
    coords1 = []

    if 'shading' not in symbols:
        shading = "flat"
    else:
        shading = symbols['shading'][1]

    # print(symbols)
    # print(commands)
    for index in range(len(frames)):
        print(str(index)+","+str(len(frames)))
        for knob in frames[index].keys():
            symbols[knob][1] = frames[index][knob]
        for command in commands:
            # print (command)
            c = command['op']
            args = command['args']
            # knob_value = 1

            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect,shading)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                        args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect,shading)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                        args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect,shading)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                        args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                c_k = symbols[command['knob']][1]
                tmp = make_scale(args[0]*c_k, args[1]*c_k, args[2]*c_k)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                c_k = 1
                if command['knob'] != None:
                    c_k = symbols[command['knob']][1]
                theta = args[1] * (math.pi/180) * c_k
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            # elif c == 'save':
            #     save_extension(screen, args[0])
            # end operation loop
        if len(frames) > 1:
            save_extension(screen, "anim/"+name+"%03d"%index+".png")
        else:
            save_extension(screen,name)
        # Reset Screen, origin stack
        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
    if len(frames) > 1:
        make_animation(name)
