local script=debug.getinfo(1,'S').source:sub(2)
local root=(script:match('^(.*[/\\])') or './')..'../'
local Style=dofile(root..'overload/mod/class/CheckerTokenStyle.lua')
local cases={
 {100,100,0,1,'full'}, {75,100,0,.75,'three quarters'}, {50,100,0,.5,'half'},
 {25,100,0,.25,'quarter'}, {5,100,0,.05,'almost depleted'}, {0,100,0,0,'zero'},
 {120,100,0,1,'overheal capped'}, {-10,100,0,0,'below death threshold'},
 {100,100,-100,1,'negative-life full'}, {0,100,-100,.5,'zero is alive with negative death threshold'},
 {-50,100,-100,.25,'negative life still has capacity'}, {-100,100,-100,0,'negative death threshold'},
 {0,0,0,0,'empty span'}, {10,10,10,0,'degenerate death threshold'},
}
for _,c in ipairs(cases) do
 local actor={life=c[1],max_life=c[2],die_at=c[3]}
 assert(math.abs(Style.lifeFraction(actor)-c[4])<1e-9,c[5])
 assert(actor.life==c[1] and actor.max_life==c[2] and actor.die_at==c[3],'display must not change life rules')
end
assert(Style.lifeFraction{life=50,max_life=100}==.5,'native omitted die_at defaults to zero')
print('radial_health: 15 health states and non-mutation checks passed')
