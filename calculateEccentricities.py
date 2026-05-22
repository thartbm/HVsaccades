import numpy as np


def cart2pol(x, y, units='deg'):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    if units == 'deg':
        phi = np.rad2deg(phi)
    return(phi, rho)

def pol2cart(phi, rho, units='deg'):
    if units == 'deg':
        phi = np.deg2rad(phi)
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return x, y


# # # # # # # # # # # # # # # # # #
# HERE WE STORE ALL THE LOCATIONS
dot_locations = {'x':[], 'y':[]}

# # # # # # # # # # # # # # # # # #
# THIS IS ONE OF MY BLIND SPOTS
bs_pos_cart =	[15.36,-2.90]
size =	[5.73,6.20]

# IT'S IN THE RIGHT HEMIFIELD:
mult_fact = 1

lax = np.max(size)

test_dist = 3 + lax + 3
bs_dist = sum(np.array(bs_pos_cart)**2)**0.5
margin = 2

# print(bs_dist)

alpha = np.arcsin(((test_dist+margin)/2)/bs_dist) * 2 * 180/np.pi

# print(alpha)

bs_pos_pol = cart2pol(bs_pos_cart[0], bs_pos_cart[1], units='deg')

# print(bs_pos_pol)

ad_pos_pol = [bs_pos_pol[0] + (alpha * mult_fact), bs_dist]
ad_pos_cart = pol2cart(bs_pos_pol[0] + (alpha * mult_fact), bs_dist, units='deg')

# print(ad_pos_pol)
# print(ad_pos_cart)

bs_pos = bs_pos_cart
ad_pos = ad_pos_cart

for ori in [0,90]:

    bs_tilt = ori
    temp_pos = pol2cart(bs_tilt, test_dist/2, units='deg')
    point1pos = [bs_pos[0] + temp_pos[0], bs_pos[1] + temp_pos[1]]
    point2pos = [bs_pos[0] - temp_pos[0], bs_pos[1] - temp_pos[1]]

    dot_locations['x'].append(point1pos[0])
    dot_locations['y'].append(point1pos[1])
    dot_locations['x'].append(point2pos[0])
    dot_locations['y'].append(point2pos[1])

    ad_tilt = ori
    temp_pos = pol2cart(ad_tilt, test_dist/2, units='deg')
    point1pos = [ad_pos[0] + temp_pos[0], ad_pos[1] + temp_pos[1]]
    point2pos = [ad_pos[0] - temp_pos[0], ad_pos[1] - temp_pos[1]]

    dot_locations['x'].append(point1pos[0])
    dot_locations['y'].append(point1pos[1])
    dot_locations['x'].append(point2pos[0])
    dot_locations['y'].append(point2pos[1])

print(dot_locations)