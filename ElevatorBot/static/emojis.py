from typing import TYPE_CHECKING

from naff import CustomEmoji
from naff.client.errors import Forbidden

if TYPE_CHECKING:
    from ElevatorBot.discordEvents.base import ElevatorClient


class __ElevatorEmojis:
    """To add an emoji add it to the class variables"""

    def __init__(self):
        # !!!
        # Either the moji id must be correct, or the emoji name on discord must be the same as in the class here
        # !!!

        # DESCEND [BL]

        self.kinetic: CustomEmoji | int = 906180170875031562
        self.stasis: CustomEmoji | int = 897797463799369769
        self.arc: CustomEmoji | int = 897797463933583401
        self.thermal: CustomEmoji | int = 897797463937798174
        self.void: CustomEmoji | int = 897797464013307905

        self.unstoppable: CustomEmoji | int = 897797463807774752
        self.barrier: CustomEmoji | int = 897797463988142091
        self.overload: CustomEmoji | int = 897797463988142090

        self.auto_rifle: CustomEmoji | int = 906180170778546226
        self.shotgun: CustomEmoji | int = 906180170971484220
        self.machinegun: CustomEmoji | int = 906180170833100820
        self.hand_cannon: CustomEmoji | int = 906180170979881000
        self.rocket_launcher: CustomEmoji | int = 906180170799521812
        self.fusion_rifle: CustomEmoji | int = 906180170929565777
        self.sniper_rifle: CustomEmoji | int = 906180170807906366
        self.pulse_rifle: CustomEmoji | int = 906180170820485190
        self.scout_rifle: CustomEmoji | int = 906180170858250261
        self.sidearm: CustomEmoji | int = 906180170833096774
        self.sword: CustomEmoji | int = 906180170929565776
        self.fusion_rifle_line: CustomEmoji | int = 906180170807906365
        self.grenade_launcher: CustomEmoji | int = 906180170405249025
        self.submachine_gun: CustomEmoji | int = 906180170799521815
        self.trace_rifle: CustomEmoji | int = 912989912251367444
        self.bow: CustomEmoji | int = 906180170799538206
        self.glaive: CustomEmoji | int = 940637142470778890

        self.primary: CustomEmoji | int = 906180170887622656
        self.special: CustomEmoji | int = 906180170858250260
        self.heavy: CustomEmoji | int = 906180170451410985

        # DESCEND [WQ]
        self.tile_left: CustomEmoji | int = 930155671960313946
        self.tile_mid: CustomEmoji | int = 930155672048377906
        self.tile_right: CustomEmoji | int = 930155672006459502
        self.enter: CustomEmoji | int = 930155672123883540
        self.circle: CustomEmoji | int = 930155671947735090
        self.question: CustomEmoji | int = 930155672052580372
        self.settings: CustomEmoji | int = 930155672014843904

        self.yes: CustomEmoji | int = 930155671930962001
        self.no: CustomEmoji | int = 930155672014819388
        self.thumps_up: CustomEmoji | int = 930155671784128584
        self.thumps_down: CustomEmoji | int = 930155671989657600

        self.discord: CustomEmoji | int = 930155671649918987
        self.descend_logo: CustomEmoji | int = 930153190274531368
        self.elevator_logo: CustomEmoji | int = 930155671784128583
        self.ping: CustomEmoji | int = 930167151908765696

        self.destiny: CustomEmoji | int = 930155672006430750
        self.raid: CustomEmoji | int = 622050515194347552

        self.progress_four_quarter: CustomEmoji | int = 930110935803252806
        self.progress_three_quarter: CustomEmoji | int = 930146155466223646
        self.progress_two_quarter: CustomEmoji | int = 930110935849402448
        self.progress_one_quarter: CustomEmoji | int = 930146155340369951
        self.progress_zero_edge: CustomEmoji | int = 930110935887138836
        self.progress_zero: CustomEmoji | int = 930110935887138837

        # DESCEND [Other]
        self.among_us: CustomEmoji | int = 905844106914332682
        self.barotrauma: CustomEmoji | int = 905846654316445758
        self.gta: CustomEmoji | int = 905847049059197009
        self.valorant: CustomEmoji | int = 905849958601744385
        self.lol: CustomEmoji | int = 905843726583226449
        self.eft: CustomEmoji | int = 905846654211620865
        self.minecraft: CustomEmoji | int = 905846654211620866
        self.new_world: CustomEmoji | int = 900640805784522762

        self.warlock: CustomEmoji | int = 830747907488612402
        self.hunter: CustomEmoji | int = 830747907829006346
        self.titan: CustomEmoji | int = 830747907576823808
        self.light_level: CustomEmoji | int = 830750430816108564

        self.join: CustomEmoji | int = 850000522101391400
        self.leave: CustomEmoji | int = 850000522048045106
        self.backup: CustomEmoji | int = 850000522107027466

        self.zoom: CustomEmoji | int = 906503515642425396

        self.first_place: CustomEmoji | int = 933410347111551056
        self.second_place: CustomEmoji | int = 933410347195445268
        self.third_place: CustomEmoji | int = 933410347287724072

        # DESCEND [SK]
        self.glimmer: CustomEmoji | int = 967764582514970654
        self.legendary_shards: CustomEmoji | int = 967764636491460718
        self.bright_dust: CustomEmoji | int = 967764684910501888
        self.spoils_of_conquest: CustomEmoji | int = 967764715562487868
        self.raid_banner: CustomEmoji | int = 967766506861637632
        self.sweaty_confetti: CustomEmoji | int = 967764751209873458
        self.synthweave_strap_hunter: CustomEmoji | int = 967764790523084820
        self.synthweave_plate_titan: CustomEmoji | int = 967764821166669915
        self.synthweave_bolt_warlock: CustomEmoji | int = 967764881250066442
        self.resonant_alloy: CustomEmoji | int = 967764995867815986
        self.drowned_alloy: CustomEmoji | int = 967765028931526676
        self.ascendant_alloy: CustomEmoji | int = 967765063798759444
        self.upgrade_module: CustomEmoji | int = 967765090562637874
        self.enhancement_core: CustomEmoji | int = 967765115027992677
        self.enhancement_prism: CustomEmoji | int = 967765139937972254
        self.ascendant_shard: CustomEmoji | int = 967765168228540446

    async def init_emojis(self, client: "ElevatorClient"):
        """Runs on startup to get the emojis we use"""

        emojis = []

        # get all emojis from the emote servers
        for guild_id in [768902336914391070, 724676552175910934, 556418279015448596, 697720309847162921]:
            try:
                if guild := await client.fetch_guild(guild_id):
                    emojis.extend(await guild.fetch_all_custom_emojis())
            except Forbidden:
                # no access to descend servers
                continue

        # loop through all class attributes
        # this is inefficient but dynamic and only called once
        for attr, value in self.__dict__.items():
            if isinstance(value, int):
                found_emoji = "🙃"
                # loop through found emojis
                for emoji in emojis:
                    if (emoji.id == value) or (emoji.name.lower() == attr.lower()):
                        found_emoji = emoji
                        break
                setattr(self, attr, found_emoji)


custom_emojis: __ElevatorEmojis = __ElevatorEmojis()
