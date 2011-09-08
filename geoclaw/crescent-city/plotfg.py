"""
Plot fixed grid output.
fgno refers to the number of the fixed grid
Execute from Unix command line via:
    $ python plotfg.py 1
to plot fixed grid number 1, for example.
Specify output directory other than _output by adding the outdir to this line:
    $ python plotfg.py 1 _output-05

    
Or from within Python or IPython:
    >>> import plotfg
    >>> plotfg.fgloop(fgno=1, outdir='_output-05')
"""

from pylab import *
from pyclaw.plotters import geoplot, colormaps
import os
from numpy import ma

drytol = 1.e-4   # For Monai wave tank!!!!!!!!!!!
exposed_tol = 1.e-4  # for plotting region that goes dry


def plotfg(fgno, frameno, outdir='_output'):
#    fname = "fort.fg%s_%s" % (str(fgno).zfill(2), str(frameno).zfill(4))
    fname = "fort.q%s_%s" % (str(fgno).zfill(2), str(frameno).zfill(4))
    fname = os.path.join(outdir,fname)
    if not os.path.exists(fname):
        print "*** Did not find file ",fname," in directory ",outdir
        raise IOError("Missing fixed grid output file")
    
    print "Plotting ",fname

    # Read parameters from header:

    file = open(fname,'r')

    line = file.readline()
    t = float(line.split()[0])
    print 't = %s' % t

    line = file.readline()
    mx = int(line.split()[0])
    print 'mx = %s' % mx

    line = file.readline()
    my = int(line.split()[0])
    print 'my = %s' % my

    line = file.readline()
    xlow = float(line.split()[0])
    print 'xlow = %s' % xlow

    line = file.readline()
    ylow = float(line.split()[0])
    print 'ylow = %s' % ylow

    line = file.readline()
    xhi = float(line.split()[0])
    print 'xhi = %s' % xhi

    line = file.readline()
    yhi = float(line.split()[0])
    print 'yhi = %s' % yhi
    file.close()



    x = linspace(xlow,xhi,mx+1)
    y = linspace(ylow,yhi,my+1)
    dx = x[1]-x[0]
    dy = y[1]-y[0]
    xcenter = x[:-1] + dx/2.
    ycenter = y[:-1] + dy/2.

    d = loadtxt(fname, skiprows=8)

    h = reshape(d[:,0], (my,mx))
    B = reshape(d[:,3], (my,mx))
    eta = reshape(d[:,4], (my,mx))
    surface = ma.masked_where(isnan(eta),eta)
    land = ma.masked_where(h>drytol,B)


    # plot commands: 
    # ==============

    # ===================================================
    # Adjust these:

    # Define function to plot topo contours for use in multiple places:
    def add_contours():
        contour(xcenter,ycenter,B,20,colors='k')
        contour(xcenter,ycenter,B,[0.],colors='b',linewidths=2)

    # Set colormaps:
    water_cmap = geoplot.tsunami_colormap
    land_cmap = geoplot.land_colors
    seafloor_cmap = geoplot.seafloor_colormap
    
    # ===================================================

    figure(150)
    clf()
    
    if ma.count(surface) != 0:
        pcolormesh(x,y,surface,cmap=water_cmap)
        #clim((-0.02,0.02))
        colorbar()
    
    if ma.count(land) != 0:
        pcolormesh(x,y,land,cmap=land_cmap)
        #clim((-0.02,0.02))
    
    add_contours()
    
    
    #xlim((xlow,xhi))
    #ylim((ylow,yhi))

    ncols = d.shape[1]
    axis('scaled')
    title('Surface on fixed grid %s at time = %8.5f' % (fgno,t))
    
    return_fg = True  # return all the fg arrays for other purposes?
    if return_fg:
        fg = empty((my,mx,ncols), dtype=float)
        for col in range(ncols):
            fg[:,:,col] = reshape(d[:,col],(my,mx))
    
    if ncols > 5:
        etamin = reshape(d[:,5], (my,mx))
        etamax = reshape(d[:,6], (my,mx))

        #etamax2 = where(B<0, 1., etamax)
        etamax2 = where(B<0, 1., etamax)
        
        # Add red contour of maximum eta
        #contour(xcenter,ycenter,etamax2,[drytol],colors='r',linewidths=2)
        
        # Add brown contour of minimum eta
        #contour(xcenter,ycenter,etamin-B,[exposed_tol],colors=([.9,.8,.2],),linewidths=2)

        # Determine exposed and inundatated regions:

        exposed = ma.masked_where(((B>0) | (etamin > B+exposed_tol)), etamin)
        inundated = ma.masked_where(((B<0) | (etamax < B)), etamax)

        figure(151)
        clf()
        
        if ma.count(inundated) != 0:
            pcolormesh(x,y,inundated,cmap=geoplot.tsunami_colormap)
            clim((-0.02,0.02))
            colorbar()
        add_contours()
        # Add red contour of maximum eta
        #contour(xcenter,ycenter,etamax2,[drytol],colors='r',linewidths=2)
        title("Inundated region for t <= %8.5f" % t)
        axis('scaled')

        figure(152)
        clf()
        
        if ma.count(exposed) != 0:
            pcolormesh(x,y,exposed,cmap=seafloor_cmap)
            #clim((-0.02,0.02))
            colorbar()
        add_contours()
        # Add brown contour of minimum eta
        #contour(xcenter,ycenter,etamin-B,[exposed_tol],colors=([.9,.8,.2],),linewidths=2)
        title("Exposed seabed for t <= %8.5f" % t)
        axis('scaled')
            
            
        return fg
        
    
def fgloop(fgno=1, outdir='_output'):
    for frameno in range(1,100):
        try:
            fg = plotfg(fgno, frameno, outdir)
        except IOError:
            break
        ans = raw_input("Hit return for next time, q to quit, s to savefig... ")
        if ans=='s':
            fname = 'FixedGrid%sFrame%s.png' %  (str(fgno).zfill(2), str(frameno).zfill(4))
            savefig(fname)
            print "Saved figure as ",fname
            ans = raw_input("Hit return for next time, q to quit, s to savefig... ")
            
        if ans=='q':
            break

            

if __name__ == "__main__":
    # if executed at the Unix command line....
    import sys
    args = sys.argv[1:]   # any command line arguments
    fgloop(*args)
