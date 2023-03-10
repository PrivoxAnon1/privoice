class Skill:
    # we expect a json file in each skill base dir
    # which contains the following information.
    def __init__(self, **kwargs):
        self.search_terms = '' #(time, date, default)
        self.skill_id = ''     #(must be unique like pva_time or pva_date)
        self.name = ''         #(privox default date time skill or joe's joke skill)
        self.description = ''
        self.repo = ''         #name of repo found in
        self.base_dir = ''     #somewhere in the tmp_skills/ dir
        self.__dict__.update(kwargs)

    def __str__(self):
        return "ID:%s, NAME:%s, REPO:%s, BASE:%s, TERMS:%s, DESC:%s" % (self.skill_id, self.name, self.repo, self.base_dir, self.search_terms, self.description)

