# Current Projects
___ 
### Integrate Location from UTM.campaign into DAR

#### Week of *May 13th, 2020*

***Pre-DAR Work***

1. Reflect Campaign Location on Ad Spend
   1. Create Reference field for campaign location on advertisement.amount 

***DAR Work***

2. Restructure how DAR reflects CAD and Location
   1. Move CAD to it's own field, seperate from status selection
   2. Create Selection field for Location, so that each DAR record  *can be grouped by location*
      ~~1. Note: OMG I am so stupid. Bringing Location over should be really easy, the model for it is the cohort date field.~~
      [update: location already exists on res_partner as team_id ]
      1. Note: I remember now, the issue I was having before is that a new line is not being created per unique location. Therefore I need to modify the DAR to create new lines based (not ONLY on unique_date , but,) on unique_combination of unique_date & unique_location).
         1. For Now I will keep location as a char field, this shouldn't prevent grouping by location, though it'll probably  make it more sloppy. Depending on how "sloppy" it is I might switch it to a selection fie
3. Run actions to repopulate DAR.

