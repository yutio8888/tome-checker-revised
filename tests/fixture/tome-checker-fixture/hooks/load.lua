local Fixture=require 'mod.class.CheckerFixture'
class:bindHook('ToME:birthDone',function(self)
 if not Fixture.enabled() then return end
 game.checker_ready=true
 game.checker_hero=game.player
 print('[CheckerFixture] BIRTH',game.player.descriptor.subrace,game.player.descriptor.sex,game.player.descriptor.subclass,game.player.descriptor.difficulty,game.zone.short_name)
end)
class:bindHook('ToME:runDone',function(self)
 if not Fixture.enabled() or not game.player or not game.level then return end
 game.checker_ready=true
 game.checker_hero=game.checker_hero or game.player
end)
